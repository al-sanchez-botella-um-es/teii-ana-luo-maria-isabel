""" Time Series Finance Client classes """


import datetime as dt
import logging
from typing import Optional, Union

import pandas as pd

from teii.finance import (FinanceClient, FinanceClientInvalidData,
                          FinanceClientParamError)


class TimeSeriesFinanceClient(FinanceClient):
    """ Wrapper around the AlphaVantage API for Time Series Weekly Adjusted.

        Source:
            https://www.alphavantage.co/documentation/
            (TIME_SERIES_WEEKLY_ADJUSTED)
    """

    _data_field2name_type = {
        "1. open":                  ("open",     "float"),
        "2. high":                  ("high",     "float"),
        "3. low":                   ("low",      "float"),
        "4. close":                 ("close",    "float"),
        "5. adjusted close":        ("aclose",   "float"),
        "6. volume":                ("volume",   "int"),
        "7. dividend amount":       ("dividend", "float")
    }

    def __init__(self, ticker: str,
                 api_key: Optional[str] = None,
                 logging_level: Union[int, str] = logging.WARNING) -> None:
        """ TimeSeriesFinanceClient constructor. """

        super().__init__(ticker, api_key, logging_level)

        self._build_data_frame()

    def _build_data_frame(self) -> None:
        """ Build Panda's DataFrame and format data. """
        # TODO
        #   Comprueba que no se produce ningún error y genera excepción
        #   'FinanceClientInvalidData' en caso contrario

        # Build Panda's data frame
        data_frame = pd.DataFrame.from_dict(self._json_data, orient='index',
                                            dtype='float')

        # Rename data fields
        data_frame = data_frame.rename(columns={key: name_type[0]
                                                for key, name_type in self.
                                                _data_field2name_type.items()})

        # Set data field types
        data_frame = data_frame.astype(dtype={name_type[0]: name_type[1]
                                              for key, name_type in self.
                                              _data_field2name_type.items()})

        # Set index type
        data_frame.index = data_frame.index.astype("datetime64[ns]")

        # Sort data
        self._data_frame = data_frame.sort_index(ascending=True)

    def _build_base_query_url_params(self) -> str:
        """ Return base query URL parameters.

        Parameters are dependent on the query type:
            https://www.alphavantage.co/documentation/
        URL format:
            https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=TICKER&outputsize=full&apikey=API_KEY&data_type=json
        """
        return (
            f"function=TIME_SERIES_WEEKLY_ADJUSTED"
            f"&symbol={self._ticker}"
            f"&outputsize=full"
            f"&apikey={self._api_key}"
            )


    @classmethod
    def _build_query_data_key(cls) -> str:
        """ Return data query key. """

        return "Weekly Adjusted Time Series"

    def _validate_query_data(self) -> None:
        """ Validate query data. """

        try:
            assert self._json_metadata["2. Symbol"] == self._ticker
        except Exception as e:
            raise FinanceClientInvalidData(
                "Metadata field '2. Symbol' not found") from e
        else:
            self._logger.info(
                f"Metadata key '2. Symbol' = '{self._ticker}' found")

    def weekly_price(self,
                     from_date: Optional[dt.date] = None,
                     to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly close price from 'from_date' to 'to_date'. """

        assert self._data_frame is not None

        series = self._data_frame['aclose']

        # EJERCICIO 'PRICE':
        #   Comprueba que from_date <= to_date y genera excepción
        #   'FinanceClientParamError' en caso de error

        # FIXME: type hint error
        if from_date is not None and to_date is not None:
            series = series.loc[from_date:to_date]   # type: ignore

        # return series
        # si no hay fechas, devolvemos la serie completa
        if from_date is None or to_date is None:
            return series

        # 2. Validar tipos
        if not isinstance(from_date, dt.date) or not isinstance(to_date,
                                                                dt.date):
            raise FinanceClientParamError(
                "Las fechas deben ser objetos datetime.date")

        # 3. Validar orden
        if from_date > to_date:
            raise FinanceClientParamError(
                "from_date no puede ser posterior a to_date")

        # 4. Filtrar
        return series.loc[from_date:to_date]   # type: ignore

    def weekly_volume(self,
                      from_date: Optional[dt.date] = None,
                      to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly volume from 'from_date' to 'to_date'. """

        assert self._data_frame is not None

        series = self._data_frame['volume']

        # EJERCICIO 'VOLUME':
        #   Comprueba que from_date <= to_date y genera excepción
        #   'FinanceClientParamError' en caso de error

        # 1. Si no hay fechas -> devolver serie completa
        if from_date is None or to_date is None:
            return series

        # 2. Validar tipos
        if not isinstance(from_date, dt.date) or not isinstance(to_date,
                                                                dt.date):
            raise FinanceClientParamError(
                "Las fechas deben ser objetos datetime.date"
            )

        # 3. Validar orden
        if from_date > to_date:
            raise FinanceClientParamError(
                "from_date no puede ser posterior a to_date"
            )

        # 4. Filtrado correcto (sin validar año)
        return series.loc[from_date:to_date]  # type: ignore


    def yearly_dividends(self,
                         from_year: Optional[int] = None,
                         to_year: Optional[int] = None) -> pd.Series:
        """ Devuelve el dividendo total anual de from_year y to_year del ticket elegido"""

        assert self._data_frame is not None

        # validar tipos y rangos de parámetros
        if from_year is not None and not isinstance(from_year, int):
            raise FinanceClientParamError("from_year debe ser un número entero (int)")

        if to_year is not None and not isinstance(to_year, int):
            raise FinanceClientParamError("to_year debe ser un número entero (int)")

        if from_year is not None and to_year is not None and from_year > to_year:
            raise FinanceClientParamError("from_year no puede ser posterior a to_year")

        # extraemos el dividendo
        series = self._data_frame['dividend']

        # Agrupamos por el año del índice Datetime y sumamos los dividendos
        annual_dividends = series.groupby(series.index.year).sum()  # índice de años

        # Filtramos por el rango de años solicitado
        if from_year is not None:
            annual_dividends = annual_dividends[annual_dividends.index >= from_year]
        if to_year is not None:
            annual_dividends = annual_dividends[annual_dividends.index <= to_year]

        return annual_dividends

    def highest_weekly_variation(self,
                                 from_date: Optional[dt.date] = None,
                                 to_date: Optional[dt.date] = None) -> Optional[tuple[dt.date, float, float, float]]:
        """ Devolver (date, high, low, variation) para la semana con la mayor variación. """

        assert self._data_frame is not None

        # Validaciones de tipo
        if from_date is not None and not isinstance(from_date, dt.date):
            raise FinanceClientParamError("from_date debe ser un objeto datetime.date")
        if to_date is not None and not isinstance(to_date, dt.date):
            raise FinanceClientParamError("to_date debe ser un objeto datetime.date")

        # Validaciones de rango
        if from_date is not None and to_date is not None:
            if from_date > to_date:
                raise FinanceClientParamError("from_date no puede ser posterior a to_date")

        # Copiamos el dataframe en una copia para no modificarlo
        df_recortado = self._data_frame

        # Aplicamos el filtro de fechas
        if from_date is not None:
            df_recortado = df_recortado[df_recortado.index.date >= from_date]
        if to_date is not None:
            df_recortado = df_recortado[df_recortado.index.date <= to_date]

        # Si con el rango de fechas vacía el DataFrame, devolvemos None de forma segura
        if df_recortado.empty:
            return None

        # Calculamos la variación (high - low) para todas las filas filtradas
        variacion = df_recortado['high'] - df_recortado['low']

        # Encontramos la fecha (idmax) donde la variación es la más alta
        fecha_max_var = variacion.idxmax()

        # Extraemos valores para construir la tupla
        fila_max = df_recortado.loc[fecha_max_var]

        high_val = float(fila_max['high'])
        low_val = float(fila_max['low'])
        var_val = float(high_val - low_val)

        # Convertimos el índice DatetimeIndex de Pandas a un objeto datetime.date de python
        fecha_nativa = fecha_max_var.date()

        return (fecha_nativa, high_val, low_val, var_val)
