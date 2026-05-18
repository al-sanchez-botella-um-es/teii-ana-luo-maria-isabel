""" Unit tests for teii.finance.timeseries module """


import datetime as dt
import pandas as pd
import pytest
import requests
from pandas.testing import assert_series_equal
from unittest.mock import Mock
from typing import Any
from teii.finance import (FinanceClientInvalidAPIKey, TimeSeriesFinanceClient,
                          FinanceClientParamError, FinanceClientAPIError,
                          FinanceClientInvalidData)

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
    # EJERCICIO 'VOLUME':
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)
    # Caso 1: tipo incorrecto
    with pytest.raises(FinanceClientParamError):
        fc.weekly_volume("2026-01-01", dt.date(2026, 12, 31))

    # Caso 2: from_date > to_date
    with pytest.raises(FinanceClientParamError):
        fc.weekly_volume(
            dt.date(2026, 12, 31),
            dt.date(2026, 1, 1)
        )
    pass


def test_weekly_volume_no_dates(api_key_str,
                                mocked_requests,
                                pandas_series_NVDA_volumes):
    # EJERCICIO 'VOLUME':
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    vs = fc.weekly_volume()

    # Debe tener el mismo número de semanas que la serie completa
    assert vs.count() == pandas_series_NVDA_volumes.count()

    # Comparación exacta
    assert_series_equal(vs, pandas_series_NVDA_volumes)
    pass


def test_weekly_volume_dates(api_key_str,
                             mocked_requests,
                             pandas_series_NVDA_volumes_filtered):
    # EJERCICIO 'VOLUME':
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    vs = fc.weekly_volume(
        dt.date(2025, 4, 1),
        dt.date(2026, 3, 31)
    )

    # Debe tener el mismo número de semanas que la serie filtrada
    assert vs.count() == pandas_series_NVDA_volumes_filtered.count()

    # Comparación exacta
    assert_series_equal(vs, pandas_series_NVDA_volumes_filtered)

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
    assert_series_equal(ps_resultado_recortado, pandas_series_IBM_dividends,
                        check_names=False, check_index_type=False, atol=0.02)


def test_yearly_dividends_dates(api_key_str: str,
                                mocked_requests,
                                pandas_series_IBM_dividends: pd.Series) -> None:  # Usamos la serie completa 
    """
    Verifica que yearly_dividends(from_year, to_year) filtra y calcula correctamente
    """
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    year_start = 2022
    year_end = 2025

    ps_resultado = fc.yearly_dividends(from_year=year_start, to_year=year_end)
    # Filtramos dinámicamente la serie completa en memoria para los años del 2022 a 2025)
    esperado_filtrado = pandas_series_IBM_dividends[
        (pandas_series_IBM_dividends.index >= year_start) &
        (pandas_series_IBM_dividends.index <= year_end)
    ]
    # Comparamos la igualdad resultados
    assert_series_equal(ps_resultado, esperado_filtrado,
                        check_names=False,  # ignora como se llaman las series o sus columnas.
                        check_index_type=False,  # Evita fallo si índices de las series usan distintos números enteros
                        check_dtype=False,  # Hace lo mismo que el anterior, pero aplicado a los valores de la serie
                        atol=0.02)  # pequeñas diferencias decimales, acepta 0.02 de variacion


def test_yearly_dividends_invalid_params(api_key_str: str,
                                         mocked_requests) -> None:
    """ Verifica que lanza FinanceClientParamError ante parámetros inválidos. """
    fc = TimeSeriesFinanceClient("IBM", api_key_str)

    # Caso 1: Año de inicio posterior al año de fin
    with pytest.raises(FinanceClientParamError):
        fc.yearly_dividends(from_year=2026, to_year=2021)

    # Caso 2: El tipo de parámetro no es un entero (int)
    with pytest.raises(FinanceClientParamError):
        fc.yearly_dividends(from_year="2020", to_year=2025)  # type: ignore


# --- EJERCICIO [VARIATION] ---


def test_highest_weekly_variation_no_dates(api_key_str, mocked_requests):
    """ Verifica el cálculo de la mayor variación para todo el histórico de NVDA. """
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    resultado = fc.highest_weekly_variation()

    # Verificamos que no devuelva None
    # Tiene que ser tupla de 4 elementos
    assert resultado is not None
    assert isinstance(resultado, tuple)
    assert len(resultado) == 4

    # Comprobamos los tipos de datosdevueltos
    assert isinstance(resultado[0], dt.date)
    assert isinstance(resultado[1], float)
    assert isinstance(resultado[2], float)
    assert isinstance(resultado[3], float)

    # La variación debe ser exactamente high - low
    assert resultado[3] == pytest.approx(resultado[1] - resultado[2], abs=0.01)


def test_highest_weekly_variation_dates(api_key_str, mocked_requests):
    """ Verifica el cálculo acotando un intervalo mínimo de fechas en 2026. """
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    # Usamos un rango de fechas que sí exista en el JSON de NVDA (Marzo 2026)
    from_date = dt.date(2026, 3, 1)
    to_date = dt.date(2026, 3, 31)

    resultado = fc.highest_weekly_variation(from_date=from_date, to_date=to_date)

    assert resultado is not None
    # Comprobamos que la fecha elegida esté dentro del rango solicitado
    assert from_date <= resultado[0] <= to_date
    assert resultado[3] == pytest.approx(resultado[1] - resultado[2], abs=0.01)


def test_highest_weekly_variation_invalid_params(api_key_str, mocked_requests):
    """ Verifica que salten las excepciones correctas ante entradas erróneas. """
    fc = TimeSeriesFinanceClient("NVDA", api_key_str)

    # Caso 1: Fechas invertidas
    with pytest.raises(FinanceClientParamError):
        fc.highest_weekly_variation(from_date=dt.date(2026, 3, 31), to_date=dt.date(2026, 3, 1))

    # Caso 2: Parámetro con tipo incorrecto (String en lugar de datetime.date)
    with pytest.raises(FinanceClientParamError):
        fc.highest_weekly_variation(from_date="2026-03-01", to_date=dt.date(2026, 3, 31))  # type: ignore
