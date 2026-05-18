""" Unit tests for teii.finance.timeseries module """


import datetime as dt

import pytest
from pandas.testing import assert_series_equal

from teii.finance import (FinanceClientInvalidAPIKey, TimeSeriesFinanceClient,
                          FinanceClientParamError)


# Cada vez que se ejecuta un test, las funciones a probar serán las que
# empiecen con 'test_'
def test_constructor_success(api_key_str,
                             mocked_requests):
    TimeSeriesFinanceClient("NVDA", api_key_str)


def test_constructor_failure_invalid_api_key():
    with pytest.raises(FinanceClientInvalidAPIKey):
        TimeSeriesFinanceClient("NVDA")


def test_weekly_price_invalid_dates(api_key_str,
                                    mocked_requests):
    # EJERCICIO 'PRICE':
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    # Caso 1: from_date > to_date
    with pytest.raises(FinanceClientParamError):
        fc.weekly_price(
            dt.date(2026, 12, 31),
            dt.date(2026, 1, 1)
        )

    # Caso 2: tipo incorrecto
    with pytest.raises(FinanceClientParamError):
        fc.weekly_price(
            "2026-01-01",
            dt.date(2026, 12, 31)
        )

    pass


def test_weekly_price_no_dates(api_key_str,
                               mocked_requests,
                               pandas_series_NVDA_prices):
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    ps = fc.weekly_price()

    assert ps.count() == 1378
    # 1999-11-12 to 2026-04-02 (1378 business weeks)

    assert ps.count() == pandas_series_NVDA_prices.count()

    assert_series_equal(ps, pandas_series_NVDA_prices)


def test_weekly_price_dates(api_key_str,
                            mocked_requests,
                            pandas_series_NVDA_prices_filtered):
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    ps = fc.weekly_price(dt.date(year=2025, month=4, day=1),
                         dt.date(year=2026, month=3, day=31))

    assert ps.count() == 52    # 2025-04-01 to 2026-03-31 (52 business weeks)

    assert ps.count() == pandas_series_NVDA_prices_filtered.count()

    assert_series_equal(ps, pandas_series_NVDA_prices_filtered)


def test_weekly_volume_invalid_dates(api_key_str,
                                     mocked_requests):
    # TODO
    pass


def test_weekly_volume_no_dates(api_key_str,
                                mocked_requests):
    # TODO
    pass


def test_weekly_volume_dates(api_key_str,
                             mocked_requests):
    # TODO
    pass
