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


def update_remote_table(db_session, table_data, rub_rate):
    """
    Inserts table data from google-table into secondary
    remote orders table with deletion of older records

    :param db_session: db_session: session obj from sqlalchemy.orm.sessionmaker
    :param table_data: list of rows from google API
    :param rub_rate: up to date rub rate
    """

    db_session.query(RemoteOrders).delete()
    db_session.commit()
    for prime_id, row in enumerate(table_data, start=1):
        order_id, price_usd, price_rub, delivery_time = google_data_row_parse(row, rub_rate)
        remote_row = RemoteOrders(
            id=prime_id,
            order_id=order_id,
            price_usd=price_usd,
            price_rub=price_rub,
            delivery_time=delivery_time,
        )
        db_session.add(remote_row)
    db_session.commit()


def update_local_table_with_new_rows(db_session, table_data, rub_rate):
    """
    Adds only new rows to local orders table from table, fetched from google

    :param db_session: db_session: session obj from sqlalchemy.orm.sessionmaker
    :param table_data: list of rows from google API
    :param rub_rate: up to date rub rate
    """
    for row in table_data:
        order_id, price_usd, price_rub, delivery_time = google_data_row_parse(row, rub_rate)
        row_exists = db_session.query(LocalOrders.order_id).filter_by(order_id=order_id).first() is not None

        if not row_exists:
            local_row = LocalOrders(
                order_id=order_id,
                price_usd=price_usd,
                price_rub=price_rub,
                delivery_time=delivery_time,
            )
            db_session.add(local_row)
    db_session.commit()


def clear_local_table(db_session):
    """
    Deletes rows from local orders table by order_id. If it is not
    present in remote table, then it was deleted from original google table.

    :param db_session: db_session: session obj from sqlalchemy.orm.sessionmaker
    """

    for current_order_id in db_session.query(LocalOrders.order_id):
        current_order_id = current_order_id[0]
        row_missing_remote = (
            db_session.query(RemoteOrders.order_id).filter_by(order_id=current_order_id).first() is None
        )

        if row_missing_remote:
            db_session.query(LocalOrders).filter(LocalOrders.order_id == current_order_id).delete()
            db_session.commit()


def main():
    """
    Main loop of db_redactor. Updates main table every n seconds, using
    google api and currency rate from cb api

    """

    # DB init
    time.sleep(3)  # Wait for postgresql to start in docker-compose
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
        before_request = time.time()
        google_data = get_spreadsheet_table()
        google_data.pop(0)  # Skip table header

        # Updating secondary remote orders table with old data removal
        update_remote_table(session, google_data, rub_rate)
        print("Updated remote")

        # Adding only new entries to local orders table
        update_local_table_with_new_rows(session, google_data, rub_rate)

        # Deleting rows from local orders table, that are already not present in google table
        clear_local_table(session)
        print("Updated local")

        # Time delay between requests if needed
        after_request = time.time()
        delta = after_request - before_request
        if delta < settings.api_time_interval:
            time.sleep(settings.api_time_interval - delta)


if __name__ == "__main__":
    main()
