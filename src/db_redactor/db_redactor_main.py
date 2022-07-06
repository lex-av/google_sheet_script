import datetime
import time
from typing import List

from api_clients.api_client_bank import check_currency_rate
from api_clients.api_google import get_spreadsheet_table
from config import settings
from db.base import DeclarativeBase, engine
from db.db_tables import RemoteOrders
from sqlalchemy.orm import sessionmaker


def google_data_row_parse(row: List, rub_rate: float):
    """
    Converts list of given values to tuple of
    types, suitable for database

    :param row: list of values
    :param rub_rate: up to date rub_rate
    :return:
    """

    order_id = (row[1],)
    price_usd = (row[2],)
    price_rub = (float(row[2]) * rub_rate,)
    delivery_time = datetime.datetime.strptime(row[3], "%d.%m.%Y")

    return order_id, price_usd, price_rub, delivery_time


def main():
    """
    Main loop of db_redactor. Updates main table every n seconds, using
    google api and currency rate from cb api

    """

    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    check_currency_rate()
    with open(settings.file_name) as f:
        file_str = f.readline()
    rub_rate = float(file_str.split("|")[0])

    while True:
        google_data = get_spreadsheet_table()
        google_data.pop(0)
        session.query(RemoteOrders).delete()

        for row in google_data:
            order_id, price_usd, price_rub, delivery_time = google_data_row_parse(row, rub_rate)
            new_line = RemoteOrders(
                order_id=order_id,
                price_usd=price_usd,
                price_rub=price_rub,
                delivery_time=delivery_time,
            )
            session.add(new_line)
        session.commit()
        print("Updated DB")
        time.sleep(2)


if __name__ == "__main__":
    main()
