



from grand_trade_auto.datafeed import datafeed_meta
from grand_trade_auto.model.exchange import Exchange



class AlphavantageDatafeed(datafeed_meta.Datafeed):


    def __init__(self, **kwargs):
        """
        """
        super().__init__(**kwargs)



    # def query_security_price(security, exchange, config_and_progress_marker):
    #     if period is less_than_daily:
    #         url, rtn_type = self.build_url_time_series_intraday(security.ticker, interval)
    #     elif period is daily:
    #         url, rtn_type = self.build_url_time_series_daily(security.ticker)

    #     results = self.call_api(url)



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

        data_from_api = parse(self.call_api(url)) # list of exchanges

        matched = []
        missing = []
        extra = []

        for e_api in data_from_api:
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
        else:
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

        # will only include valid exchanges
        data_from_api = parse(self.call_api(url)) # list of securities

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
        else:
            return matched, missing, extra
