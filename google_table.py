from pathlib import Path

import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

from config_reader import Config
from log_config import logger


def check_change(config: Config) -> list:
    first_load = False
    CREDENTIALS_FILE = config.table.credentials_file
    if not Path(CREDENTIALS_FILE).is_file():
        logger.error('Credentials file not found')
        raise FileExistsError('Credentials file not found')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, [
        'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
    ])

    httpAuth = credentials.authorize(httplib2.Http())

    drive_service = apiclient.discovery.build('drive', 'v3', http=httpAuth)

    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    if not config.table.page_token:
        logger.info('get page token')
        response = drive_service.changes().getStartPageToken().execute()
        page_token = response.get("startPageToken")
        config.table.page_token = page_token
        first_load = True

    spreadsheetId = config.table.spreadsheetId

    ranges = [f"{config.table.name_sheet}!{config.table.start_range}:{config.table.end_range}"]  #

    if has_change(drive_service, config) or first_load:
        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        return sheet_values


def has_change(service, config: Config) -> bool:
    logger.info('Check for changes')
    page_token = config.table.page_token
    were_changes_in_a_file = False

    while page_token is not None:
        response = service.changes().list(
            pageToken=config.table.page_token,
            spaces='drive'
        ).execute()

        for change in response.get('changes'):
            file_id = change.get("fileId")
            if file_id == config.table.spreadsheetId:
                were_changes_in_a_file = True
        if 'newStartPageToken' in response:
            config.table.page_token = response.get('newStartPageToken')
        page_token = response.get('nextPageToken')

    return were_changes_in_a_file
