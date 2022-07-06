import datetime
import time
from typing import List

from api_clients.api_client_bank import check_currency_rate
from api_clients.api_google import get_spreadsheet_table
from config import settings
from db.base import DeclarativeBase, engine
from db.db_tables import LocalOrders, RemoteOrders
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

    # DB init
    DeclarativeBase.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Ruble rate init
    check_currency_rate()
    with open(settings.file_name) as f:
        file_str = f.readline()
    rub_rate = float(file_str.split("|")[0])

    # Main loop for db editing/refreshing
    while True:
        # Fetching data from google API
        google_data = get_spreadsheet_table()
        google_data.pop(0)  # Skip table header

        # Updating secondary remote orders table with old data removal
        session.query(RemoteOrders).delete()
        session.commit()
        for prime_id, row in enumerate(google_data, start=1):
            order_id, price_usd, price_rub, delivery_time = google_data_row_parse(row, rub_rate)
            remote_row = RemoteOrders(
                id=prime_id,
                order_id=order_id,
                price_usd=price_usd,
                price_rub=price_rub,
                delivery_time=delivery_time,
            )
            session.add(remote_row)
        session.commit()
        print("Updated remote")

        # Adding only new entries to local orders table
        for row in google_data:
            order_id, price_usd, price_rub, delivery_time = google_data_row_parse(row, rub_rate)
            row_exists = session.query(LocalOrders.order_id).filter_by(order_id=order_id).first() is not None

            if not row_exists:
                local_row = LocalOrders(
                    order_id=order_id,
                    price_usd=price_usd,
                    price_rub=price_rub,
                    delivery_time=delivery_time,
                )
                session.add(local_row)
        session.commit()
        print("Updated local")

        # Deleting rows from local orders table, that are already not present in google table
        for current_order_id in session.query(LocalOrders.order_id):
            current_order_id = current_order_id[0]
            row_missing_remote = (
                session.query(RemoteOrders.order_id).filter_by(order_id=current_order_id).first() is None
            )

            if row_missing_remote:
                session.query(LocalOrders).filter(LocalOrders.order_id == current_order_id).delete()
                session.commit()

        time.sleep(2)


if __name__ == "__main__":
    main()
