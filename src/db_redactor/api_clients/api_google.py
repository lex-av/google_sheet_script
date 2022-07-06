from typing import List

import googleapiclient.discovery
import httplib2
from config import settings
from oauth2client.service_account import ServiceAccountCredentials


def get_spreadsheet_table() -> List:
    """
    Requests google spreadsheet table from google api
    and returns list of it's rows

    :return: spreadsheet
    """

    creds_file = settings.creds_filename
    spreadsheet_id = settings.spreadsheet_id

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        creds_file, ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )

    httpAuth = credentials.authorize(httplib2.Http())
    service = googleapiclient.discovery.build("sheets", "v4", http=httpAuth)

    values = (
        service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="A:D", majorDimension="ROWS").execute()
    )

    return values["values"]


if __name__ == "__main__":
    get_spreadsheet_table()
