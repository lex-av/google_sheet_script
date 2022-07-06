from sqlalchemy import Column, Date, Integer

from .base import DeclarativeBase


class LocalOrders(DeclarativeBase):
    """
    Main table with up to date orders data. Can be used by
    apps like tg bots or django apps
    """

    __tablename__ = "local_orders"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    order_id = Column("order_id", Integer)
    price_usd = Column("price_usd", Integer)
    price_rub = Column("price_rub", Integer)
    delivery_time = Column("delivery_time", Date)

    def __repr__(self):
        return f"{self.code}"


class RemoteOrders(DeclarativeBase):
    """
    Secondary table to fetch new data from google api. Used to help
    editing main table
    """

    __tablename__ = "local_orders"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    order_id = Column("order_id", Integer)
    price_usd = Column("price_usd", Integer)
    price_rub = Column("price_rub", Integer)
    delivery_time = Column("delivery_time", Date)

    def __repr__(self):
        return f"{self.code}"
