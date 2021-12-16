#!/usr/bin/env python3
"""
Contains the elements defining the ORM for SQL-based databases (that support
SQLAlchemy).

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import enum

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, \
        Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship



_BASE = declarative_base()



class PriceFrequency(enum.Enum):
    """
    """
    MIN1 = '1min'
    MIN5 = '5min'
    MIN10 = '10min'
    MIN15 = '15min'
    MIN30 = '30min'
    HOURLY = 'hourly'
    DAILY = 'daily'



class Market(enum.Enum):
    """
    """
    CRYPTO = 'crypto'
    STOCK = 'stock'
    FOREX = 'forex'
    FUTURES = 'futures'



class Currecny(enum.Enum):
    """
    """
    USD = 'usd'


class Security(_BASE):
    """
    """
    __tablename__ = 'security'

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_id = Column(Integer, ForeignKey('exchange.id',
            onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    ticker = Column(String(12), nullable=False)
    market = Column(Enum(Market), nullable=False)
    name = Column(String(200), nullable=False)
    company_id = Column(Integer, ForeignKey('company.id',
            onupdate='CASCADE', ondelete='RESTRICT'), nullable=False)
    currency = Column(Enum(Currecny), nullable=False)
    datafeed_src_id = Column(Integer, ForeignKey('datafeed_src.id'),
            onupdate='CASCADE', ondelete='CASCADE', nullable=False)

    exchange = relationship('Exchange')
    company = relationship('Company')
    datafeed_src = relationship('DatafeedSrc')

    UniqueConstraint('exchange_id', 'ticker', 'datafeed_src_id') # TODO: Remove datafeed, allow it to be null?



class Exchange(_BASE):
    """

    DatafeedSrc here is optional -- it's nice-to-have info, but nothing here is
    so critical that errors would be catastrophic.  It is expected to be highly
    common and consistent between datafeeds, at least for the important details.
    It only reflects the most recent datafeed to modify it.


    """
    __tablename__ = 'exchange'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    acronym = Column(String(50), nullable=False)
    datafeed_src_id = Column(Integer, ForeignKey('datafeed_src.id'),
            onupdate='CASCADE', ondelete='SET NULL')

    security = relationship('Security')
    datafeed_src = relationship('DatafeedSrc')

    UniqueConstraint('name')



class Company(_BASE):
    """
    """
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    cik = Column(String(10))
    sector = Column(String(50))
    industry_category = Column(String(50))
    industry_group = Column(String(50))
    sic = Column(String(4))
    datafeed_src_id = Column(Integer, ForeignKey('datafeed_src.id'),
            onupdate='CASCADE', ondelete='SET NULL')

    security = relationship('Security')
    datafeed_src = relationship('DatafeedSrc')

    # No unique constraint...could have companies with same name?



class StockAdjustment(_BASE):
    """
    """
    __tablename__ = 'stock_adjustment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('security.id'),
            onupdate='CASCADE', ondelete='CASCADE', nullable=False)
    date = Column(Date, nullable=False)
    factor = Column(Float, nullable=False)
    dividend = Column(Float)
    split_ratio = Column(Float)
    datafeed_src_id = Column(Integer, ForeignKey('datafeed_src.id'),
            onupdate='CASCADE', ondelete='CASCADE', nullable=False)

    security = relationship('Security')
    datafeed_src = relationship('DatafeedSrc')

    UniqueConstraint('security_id', 'date', 'datafeed_src_id')



class SecurityPrice(_BASE):
    """


    For daily and larger price frequencies, the datetime will really just be a
    date, with the time being whatever python gives when converting a date to a
    datetime (probably "midnight" with time values set to 0).


    """
    __tablename__ = 'security_price'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    security_id = Column(Integer, ForeignKey('security.id'),
            onupdate='CASCADE', ondelete='CASCADE', nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    adj_open = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=False)
    adj_high = Column(Float, nullable=False)
    adj_low = Column(Float, nullable=False)
    adj_volume = Column(Integer, nullable=False)
    intraperiod = Column(Boolean, nullable=False)
    frequency = Column(Enum(PriceFrequency), nullable=False)
    datafeed_src_id = Column(Integer, ForeignKey('datafeed_src.id'),
            onupdate='CASCADE', ondelete='CASCADE', nullable=False)

    security = relationship('Security')
    datafeed_src = relationship('DatafeedSrc')

    UniqueConstraint('security_id', 'datetime', 'datafeed_src_id')



class DatafeedSrc(_BASE):
    """
    """
    __tablename__ = 'datafeed_src'

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_parser = Column(Text, nullable=False)
    is_init_complete = Column(Boolean)
    progress_marker = Column(Text)

    UniqueConstraint(config_parser)
