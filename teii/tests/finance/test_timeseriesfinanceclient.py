""" Unit tests for teii.finance.timeseries module """


import datetime as dt
import pytest
import requests
from pandas.testing import assert_series_equal
from unittest.mock import Mock
from typing import Any
from teii.finance import FinanceClientInvalidAPIKey, TimeSeriesFinanceClient, FinanceClientInvalidData, FinanceClientAPIError

# HAY QUE AÑADIR TYPE ANNOTATIONS

# TEST 1 -> Ejercicio CONSTRUCTOR


def test_constructor_env(monkeypatch: pytest.MonkeyPatch,
                         mocked_requests: Any) -> None:
    """
    Verifica que el constructor funciona correctamente usando la
    variable de entorno TEII_FINANCE_API_KEY.
    """
    monkeypatch.setenv("TEII_FINANCE_API_KEY", "VALOR_DE_PRUEBA")

    # Ejecutamos el constructor sin pasar api_key_str
    # El objeto debe crearse con éxito al leer del entorno
    TimeSeriesFinanceClient("NVDA")

# TEST 2 -> Ejercicio CONSTRUCTOR


def test_constructor_unsuccessful_request(monkeypatch: pytest.MonkeyPatch,
                                          api_key_str: str):
    # Creamos el Mock que lanza la excepción
    mock_get = Mock(side_effect=requests.exceptions.ConnectionError("Error de red"))

    # sustituimos requests.get por el mock que acabamos de crear
    monkeypatch.setattr("teii.finance.finance.requests.get", mock_get)

    #  el constructor envuelve el FinanceClientAPIError
    with pytest.raises(FinanceClientAPIError):
        TimeSeriesFinanceClient("NVDA", api_key_str)


def test_constructor_invalid_data(monkeypatch: pytest.MonkeyPatch, api_key_str: str) -> None:
    """Verifica que el ticker NODATA (sin series temporales) lanza excepción."""
    # El mocked_requests debe estar configurado para devolver NODATA.json
    with pytest.raises(FinanceClientInvalidData):
        TimeSeriesFinanceClient("NODATA", api_key_str)


def test_constructor_success(api_key_str: str,
                             mocked_requests: Any) -> None:
    TimeSeriesFinanceClient("NVDA", api_key_str)



def test_constructor_failure_invalid_api_key():
    with pytest.raises(FinanceClientInvalidAPIKey):
        TimeSeriesFinanceClient("NVDA")



def test_weekly_price_invalid_dates(api_key_str,
                                    mocked_requests):
    # TODO
    pass


def test_weekly_price_no_dates(api_key_str,
                               mocked_requests,
                               pandas_series_NVDA_prices):
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    ps = fc.weekly_price()

    assert ps.count() == 1378   # 1999-11-12 to 2026-04-02 (1378 business weeks)

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
