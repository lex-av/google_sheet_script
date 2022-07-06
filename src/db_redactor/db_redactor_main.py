import datetime

from api_clients.api_client_bank import check_currency_rate
from api_clients.api_google import get_spreadsheet_table
from config import settings
from db.base import DeclarativeBase, engine
from db.db_tables import RemoteOrders
from sqlalchemy.orm import sessionmaker

# import time


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

    # while True:
    # time_start = time.time()
    google_data = get_spreadsheet_table()

    session.query(RemoteOrders).delete()
    new_line = RemoteOrders(
        order_id=google_data[1][1],
        price_usd=google_data[1][2],
        price_rub=float(google_data[1][2]) * rub_rate,
        delivery_time=datetime.datetime.strptime(google_data[1][3], "%d.%m.%Y"),
    )
    session.add(new_line)
    session.commit()


if __name__ == "__main__":
    main()
