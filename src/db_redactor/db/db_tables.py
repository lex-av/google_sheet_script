from sqlalchemy import Column, Date, Float, Integer

from .base import DeclarativeBase


class LocalOrders(DeclarativeBase):
    """
    Main table with up to date orders data. Can be used by
    apps like tg bots or django apps
    """

    __tablename__ = "local_orders"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    price_usd = Column(Float)
    price_rub = Column(Float)
    delivery_time = Column(Date)

    def __repr__(self):
        return f"{self.code}"


class RemoteOrders(DeclarativeBase):
    """
    Secondary table to fetch new data from google api. Used to help
    editing main table
    """

    __tablename__ = "remote_orders"

    id = Column(Integer, autoincrement=True, primary_key=True)
    order_id = Column(Integer)
    price_usd = Column(Float)
    price_rub = Column(Float)
    delivery_time = Column(Date)

    def __repr__(self):
        return f"{self.code}"
