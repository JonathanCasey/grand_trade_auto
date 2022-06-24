


import csv
import datetime as dt
from enum import Enum
import logging
import math

import pytz

from grand_trade_auto.apic import alphavantage
from grand_trade_auto.datafeed import datafeed_meta
from grand_trade_auto.model.exchange import Exchange
from grand_trade_auto.model import model_meta
from grand_trade_auto.model.security import Security



logger = logging.getLogger(__name__)



class ListingState(Enum):
    """
    """
    ACTIVE = 'active'
    DELISTED = 'delisted'



class AlphavantageDatafeed(datafeed_meta.Datafeed):


    _url_base = 'https://www.alphavantage.co/query?'

    _timezone = pytz.timezone('US/Eastern')



    # def __init__(self, **kwargs):
    #     """
    #     """
    #     super().__init__(**kwargs)



    @staticmethod
    def _convert_params_to_url_str(params):
        """
        """
        return '&'.join([f'{k}={v}' for k, v in params.items()])



    # def query_security_price(security, exchange, config_and_progress_marker):
    #     if period is less_than_daily:
    #         url, rtn_type = self.build_url_time_series_intraday(security.ticker, interval)
    #     elif period is daily:
    #         url, rtn_type = self.build_url_time_series_daily(security.ticker)

    #     results = self.call_api(url)


    @classmethod
    def _parse_datetime_with_minutes(cls, datetime_str, timezone=None):
        """
        """
        if timezone is None:
            timezone = cls._timezone
        datetime = dt.datetime.strptime(datetime_str, '%-m/%-d/%Y %-H:%M')
        return datetime.astimezone(timezone)




    def query_security_prices(self, security, start_datetime, end_datetime,
            interval, exchanges=None, allow_chunking=False, resume_data=None):
        """
        """
        assert start_datetime <= end_datetime

        if exchanges is not None:
            logger.debug('Exchanges not used by Alphavantage when getting prices.  Ignoring.')
        if interval in [
                    model_meta.PriceFrequency.MIN_1,
                    model_meta.PriceFrequency.MIN_5,
                    model_meta.PriceFrequency.MIN_15,
                    model_meta.PriceFrequency.MIN_30,
                    model_meta.PriceFrequency.HOURLY,
                ]:
            return self._query_security_prices_intraday(security,
                    start_datetime, end_datetime, interval,
                    allow_chunking, resume_data)
        else:
            raise Exception('Bad interval! Bad!')



    def _get_slices_from_datetime_range(self, start_datetime, end_datetime):
        """
        These are calculated as calendar day differences
        Assuming "extra" days are in last month
        Unknown how leap years handled -- assume spill into "extra" days of last
        month

        No, for now, will assume "year" is a loose term and it's just 30 day
        intervals
        """
        now = dt.datetime.now()
        start_delta = now - start_datetime
        start_days_ago = max(start_delta,
                dt.timedelta(days=start_delta.days)).days
        end_delta = now - end_datetime
        end_days_ago = min(end_delta,
                dt.timedelta(days=end_delta.days)).days

        start_slice_num = min(math.ceil(start_days_ago / 30), 1)
        end_slice_num = min(math.ceil(end_days_ago / 30), 1)

        if start_slice_num > 24:
            start_slice_num = 24
            logger.warning('Cannot get data older than 2 years (24*30 calendar'
                    ' days) from Alphavantage.  Truncating to starting 2 years'
                    ' ago')
        if end_slice_num > 24:
            logger.warning('Cannot get data older than 2 years (24*30 calendar'
                    ' days) from Alphavantage.  Skipping since end time is too'
                    ' long ago.')
        if start_days_ago < 0:
            start_slice_num = 1
            logger.warning('Cannot get data from the future...  Alphavantage'
                    ' start time slice truncated to today/now.')
        if end_days_ago < 0:
            end_slice_num = 1
            logger.warning('Cannot get data from the future...  Alphavantage'
                    ' end time slice truncated to today/now.')

        slice_strs = []
        for slice_num in range(end_slice_num, start_slice_num+1):
            year = math.floor((slice_num - 1) / 12) + 1
            month = ((slice_num - 1) % 12) + 1
            slice_strs.append(f'year{year}month{month}')

        return slice_strs



    def _query_security_prices_intraday(self, security, start_datetime,
            end_datetime, interval, include_raw=True, include_adjusted=True,
            allow_chunking=False, resume_data=None):
        """
        """
        # Alphavantage can't confirm exchange here, so ignore arg :(
        # This means there is no way to catch same tickers on different exchanges!
        adjusted_options = []
        if include_raw:
            adjusted_options.append(False)
        if include_adjusted:
            adjusted_options.append(True)

        if resume_data is None:
            # Want resume by datetime, not slice_str
            #  since may be resumed on different day / time
            resume_data = {
                'last_datetime': None,
            }
        # should_get_more_chunks = True

        # TODO: Add warnings for dates out of range, etc.
        slice_start_datetime = resume_data['last_datetime'] or start_datetime
        slice_strs = self._get_slices_from_datetime_range(slice_start_datetime,
                end_datetime)
        if len(slice_strs) == 0:
            slice_str = None
        else:
            slice_iter = iter(slice)
            slice_str = next(slice_iter)

        # Want to start new_last_datetime with the lowest reasonable
        new_last_datetime = resume_data['last_datetime'] or start_datetime

        data_from_api = {}
        # while resume_data is not None and should_get_more_chunks:
        while resume_data is not None and slice_str is not None:
            # slice_date = resume_data['last_date'] or start_datetime.date()
            # if slice_str is None:
            #     slice_str = self._get_slice_from_datetime(slice_date)
            #     if slice_str is None:
            #         slice_str = self._get_closest_slice_from_datetime(
            #                 slice_date)
            #     logger.warning('Skipped some dates as could not go back to start')
            # else:
            #     slice_str = self._get_newer_slice(slice_str)
            #     if slice_str is None:
            #         resume_data = None
            #         break
            for adjusted in adjusted_options:
                url = self._build_url_intraday_extended(security.ticker,
                        interval, slice_str, adjusted)
                raw_data, err = self._apic.call_api(url,
                        alphavantage.DataType.CSV)
                if err is not None:
                    logger.error(f'Error: {str(err)}')
                    continue
                csv_reader = csv.DictReader(raw_data.splitlines(), delimiter=',')
                for row in csv_reader:
                    datetime = self._parse_datetime_with_minutes(row['time'])
                    new_last_datetime = max(datetime, new_last_datetime)
                    if start_datetime <= datetime <= end_datetime and (
                            resume_data['last_datetime'] is None
                                or datetime > resume_data['last_datetime']):
                        data = {
                            'open': row['open'],
                            'close': row['close'],
                            'high': row['high'],
                            'low': row['low'],
                            'volume': row['volume'],
                        }
                        if adjusted:
                            data = {f'adj_{k}': v for k, v in data.items()}
                        else:
                            data = {f'raw_{k}': v for k, v in data.items()}
                        if datetime not in data_from_api:
                            data |= {
                                'security_id': security.id,
                                'datetime': datetime,
                                'frequency': interval,
                                # All data here is not intraperiod
                                'is_intraperiod': False,
                                'datafeed_src_id': self._get_self_model().id,
                            }
                            data_from_api[datetime] = data
                        else:
                            data_from_api[datetime] |= data

            # Moving from start to end, the slice for today must be the last slice
            # if slice_str == _get_slice_from_datetime(dt.now()):
            try:
                slice_str = next(slice_iter)
            except StopIteration:
                slice_str = None
                resume_data = None
            if allow_chunking and data_from_api:
                # If there is data, must have gotten at least 1 chunk, so pause
                slice_str = None
                # should_get_more_chunks = False
            if slice_str is not None:
                resume_data['last_datetime'] = new_last_datetime

        return data_from_api.values(), resume_data



    def _build_url_intraday_extended(self, symbol, interval, slice_str,
            adjusted=None):
        """
        """
        # TODO: Assert interval 1, 5, 15, 30, 60 min (make enum for here to convert?)
        params = {
            'function': 'LISTING_STATUS',
            'symbol': symbol,
            'interval': interval,
            'slice': slice_str,
        }
        if adjusted is not None:
            params['adjusted'] = adjusted
        return self._url_base + self._convert_params_to_url_str(params)



    def _build_url_listing_status(self, date=None, state=None):
        """
        """
        params = {
            'function': 'LISTING_STATUS',
        }
        if date is not None:
            params['date'] = dt.date.strftime(date, '%Y-%m-%d')
        if state is not None:
            params['state'] = state.value
        return self._url_base + self._convert_params_to_url_str(params)





    # For alphavantage, will get list/delist and sort exchange column for acronym
    def query_exchanges(self, include=None, exclude=None,
            include_missing=False, include_extras=False):
        """
        """
        # TODO: Have this also try returning another list that matched but
        #   updated data (if flagged to include_update -- otherwise skip checks)?
        if include is None:
            include = []
        if exclude is None:
            exclude = []

        data_from_api = {}
        for state in [ListingState.ACTIVE, ListingState.DELISTED]:
            url = self._build_url_listing_status(state=state)
            raw_data, err = self._apic.call_api(url, alphavantage.DataType.CSV)
            if err is not None:
                logger.error(f'Error: {str(err)}')
                continue
            csv_reader = csv.DictReader(raw_data.splitlines(), delimiter=',')
            for row in csv_reader:
                acronym = row['exchange']
                if acronym not in data_from_api:
                    data = {
                        'acronym': acronym,
                        'datafeed_src_id': self._df_id,
                    }
                    data_from_api[acronym] = Exchange(self._db.orm, data)

        matched = []
        missing = []
        extra = []

        for e_api in data_from_api.values():
            if e_api.acronym in [e.acronym for e in exclude]:
                continue
            # If multiple with same name, match all
            new_matches = [e for e in include if e_api.acronym == e.acronym]
            if new_matches:
                matched.extend(new_matches)
            elif include_extras or not include:
                extra.append(e_api)

        if include_missing:
            for e in include:
                if e not in matched and e not in exclude:
                    missing.append(e)

        if not include_missing and not include_extras:
            if not include:
                return matched + extra
            return matched
        return matched, missing, extra



    def query_securities(self,
            include=None, exclude=None, include_missing=False,
            include_extras=False, exchanges_allowed=None):
        """
        """
        # TODO: Have this also try returning another list that matched but
        #   updated data (if flagged to include_update -- otherwise skip checks)?
        if include is None:
            include = []
        if exclude is None:
            exclude = []
        if exchanges_allowed is None:
            exchanges_allowed = Exchange.query_direct(self._db.orm)
        exchanges_allowed_by_acronym = {e.acronym:e for e in exchanges_allowed}

        data_from_api = []
        for state in [ListingState.ACTIVE, ListingState.DELISTED]:
            url = self._build_url_listing_status(state=state)
            raw_data, err = self._apic.call_api(url, alphavantage.DataType.CSV)
            if err is not None:
                logger.error(f'Error: {str(err)}')
                continue
            csv_reader = csv.DictReader(raw_data.splitlines(), delimiter=',')
            for row in csv_reader:
                e_acronym = row['exchange']
                if e_acronym not in exchanges_allowed_by_acronym:
                    continue
                e_id = exchanges_allowed_by_acronym[e_acronym]
                data = {
                    'exchange_id': e_id,
                    'ticker': row['symbol'],
                    'name': row['name'],
                    # TODO: Parse ipo/delisting dates
                    # TODO: Parse assert type (stock vs etf)
                    'datafeed_src_id': self._df_id,
                }
                data_from_api.append(Security(self._db.orm, data))

        matched = []
        missing = []
        extra = []

        for s_api in data_from_api:
            if (s_api.exchange_id, s_api.ticker) \
                    in [(s.exchange_id, s.ticker) for s in exclude]:
                continue
            # If multiple with same name, match all
            new_matches = [s for s in include
                    if s_api.exchange_id == s.exchange_id
                        and s_api.ticker == s.ticker]
            if new_matches:
                matched.extend(new_matches)
            elif include_extras or not include:
                extra.append(s_api)

        if include_missing:
            for s in include:
                if s not in matched and s not in exclude:
                    missing.append(s)

        if not include_missing and not include_extras:
            if not include:
                return matched + extra
            return matched
        return matched, missing, extra
