import asyncio
import datetime
from http.client import HTTPException

import aiohttp
from lxml import etree
from lxml.etree import XMLSyntaxError

from config_reader import save_config
from loader import config
from log_config import logger


async def get_exchange():
    if not config.exchange.rate or config.exchange.date < datetime.datetime.today():
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(15)) as client:
                async with client.get('https://www.cbr-xml-daily.ru/daily.xml') as response:
                    data = await response.read()
                    return await asyncio.to_thread(parse_response, response=data)
        except (HTTPException, XMLSyntaxError) as exc:
            logger.error('Error request exchange rates, rates not loaded', exc_info=exc)
            return 1


def parse_response(response):
    parsed_body = etree.fromstring(response)
    rate = float(parsed_body.xpath('//Valute[@ID="R01235"]/Value/text()')[0].replace(',', '.'))
    config.exchange.rate = rate
    config.exchange.date = datetime.datetime.today()
    save_config(config)
    return rate
