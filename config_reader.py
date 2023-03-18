import datetime
from configparser import ConfigParser
from dataclasses import dataclass
from log_config import logger


@dataclass
class Table:
    credentials_file: str
    page_token: str
    spreadsheetId: str
    name_sheet: str
    start_range: str
    end_range: str


@dataclass
class Exchange:
    rate: float
    date: datetime.datetime


@dataclass
class Config:
    table: Table
    exchange: Exchange


def load_config() -> Config:
    config = ConfigParser()

    config.read('config.ini', encoding="utf-8")

    return Config(
        exchange=Exchange(
            rate=config.getfloat('Exchange', 'rate'),
            date=datetime.datetime.strptime(config.get('Exchange', 'date'), "%d.%m.%Y")
        ),
        table=Table(
            credentials_file=config.get('Table', 'credentials_file'),
            page_token=config.get('Table', 'page_token'),
            spreadsheetId=config.get('Table', 'spreadsheetId'),
            name_sheet=config.get('Table', 'name_sheet'),
            start_range=config.get('Table', 'start_range'),
            end_range=config.get('Table', 'end_range'),
        )
    )


def save_config(config_in_memory: Config) -> None:
    logger.info('save config')
    config = ConfigParser()
    config.read('config.ini', encoding="utf-8")
    config.set('Exchange', 'rate', str(config_in_memory.exchange.rate))
    config.set('Exchange', 'date', config_in_memory.exchange.date.strftime("%d.%m.%Y"))
    config.set('Table', 'page_token', config_in_memory.table.page_token)

    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
