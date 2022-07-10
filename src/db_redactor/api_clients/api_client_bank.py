import datetime
import os
import xml.etree.ElementTree as ET

import requests
from config import settings


class CentralBankApiError(Exception):
    pass


class CentralBankApiXMLError(Exception):
    pass


def _get_cb_response(cb_url: str) -> requests.Response:
    """
    Function to get currency data from CB api

    :param cb_url: CB url from settings to request data
    :return: cb api response
    """

    resp = requests.get(cb_url)
    if resp.status_code != 200:
        raise CentralBankApiError("Central Bank API is unreachable")
    return resp


def _get_currency_rate(response: requests.Response) -> float:
    """
    Parses given response's xml tree to get currency rate

    :param response: response obj crom cb api
    :return: currency rate
    """
    rate = None
    for child in ET.ElementTree(ET.fromstring(response.text)).getroot():
        if child[1].text == "USD":
            rate = float(child[4].text.replace(",", "."))

    if rate is None:
        raise CentralBankApiXMLError("Central bank API did not provide USD rate")

    return rate


def _write_dated_currency_rate(rate: float):
    """
    Writes file with today currency rate and date for
    local usage

    :param rate: Currency rate
    """

    with open(settings.file_name, "w") as file:
        # Moscow timezone
        date_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        date = date_time.date()
        file.write(f"{rate}|{date.strftime('%d.%m.%Y')}")


def check_currency_rate():
    """
    This functions is used to setup today's usd/rub rate. Creates small .txt
    file with rate and date. This function calls external api only if .txt
    file is not present or rate in this file is outdated

    """

    need_to_call_api = False
    files = os.listdir(os.getcwd())

    if settings.file_name not in files:
        need_to_call_api = True
    else:
        with open(settings.file_name) as f:
            file_str = f.readline()

        date_str = file_str.split("|")[1]
        past_date = datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
        current_date = datetime.date.today()

        if current_date > past_date:
            need_to_call_api = True

    if need_to_call_api:
        rate = _get_currency_rate(_get_cb_response(settings.cb_request_url))
        _write_dated_currency_rate(rate)
