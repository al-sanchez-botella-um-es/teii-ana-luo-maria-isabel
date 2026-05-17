""" Unit tests for teii.finance.timeseries module """


import datetime as dt
import pandas as pd
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

    # Caso 2: año incorrecto
    with pytest.raises(FinanceClientParamError):
        fc.weekly_price(
            dt.date(2025, 12, 31),
            dt.date(2026, 1, 1)
        )

    # Caso 3: tipo incorrecto
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

# EJERCICIO 'DIVIDENDS':


def test_yearly_dividends_no_dates(api_key_str: str,
                                   mocked_requests,
                                   pandas_series_IBM_dividends: pd.Series) -> None:
    """
    Verifica que yearly_dividends() sin parámetros calcula correctamente
    """
    # Inicializamos para IBM
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    ps_resultado = fc.yearly_dividends()
    # filtramos el resultado de la API para comparar solo esos mismos 5 años
    ps_resultado_recortado = ps_resultado.loc[pandas_series_IBM_dividends.index]
    # Comparamos que la serie generada sea igual a laque esperamos del CSV
    assert_series_equal(ps_resultado_recortado, pandas_series_IBM_dividends, check_names=False)


def test_yearly_dividends_dates(api_key_str: str,
                                mocked_requests,
                                pandas_series_IBM_dividends_filtered: pd.Series) -> None:
    """
    Verifica que yearly_dividends(from_year, to_year) filtra y calcula correctamente
    """
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    year_start = 2022
    year_end = 2025

    ps_resultado = fc.yearly_dividends(from_year=year_start, to_year=year_end)

    # Comparamos la igualdad resultados
    assert_series_equal(ps_resultado, pandas_series_IBM_dividends_filtered, check_names=False)


def test_yearly_dividends_invalid_params(api_key_str: str,
                                         mocked_requests) -> None:
    """
    Verifica que yearly_dividends lanza FinanceClientParamError ante 
    parámetros inválidos (años invertidos o tipos de datos incorrectos).
    """
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    # Caso 1: Año de inicio posterior al año de fin
    with pytest.raises(FinanceClientParamError):
        fc.yearly_dividends(from_year=2026, to_year=2021)

    # Caso 2: El tipo de parámetro no es un entero (int)
    with pytest.raises(FinanceClientParamError):
        fc.yearly_dividends(from_year="2020", to_year=2025)  # type: ignore
