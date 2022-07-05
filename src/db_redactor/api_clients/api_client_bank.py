import datetime
import xml.etree.ElementTree as ET

import requests


class CentralBankApiError(Exception):
    pass


class CentralBankApiXMLError(Exception):
    pass


def get_cb_response(cb_url: str) -> requests.Response:
    """
    Function to get currency data from CB api

    :param cb_url: CB url from settings to request data
    :return: cb api response
    """

    resp = requests.get(cb_url)
    if resp.status_code != 200:
        raise CentralBankApiError("Central Bank API is unreachable")
    return resp


def get_currency_rate(response: requests.Response) -> float:
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
        raise CentralBankApiXMLError("Central bank APi did not provide USD rate")

    return rate


def write_dated_currency_rate(rate: float):
    """
    Writes file with today currency rate and date for
    local usage

    :param rate: Currency rate
    """

    with open("today_rate.txt", "w") as file:
        # Moscow timezone
        date_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        date = date_time.date()
        file.write(f"{rate}|{str(date)}")
