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
        self._logger.info(
            f"Inicializando TimeSeriesFinanceClient para ticker '{ticker}'")

        self._build_data_frame()

    def _build_data_frame(self) -> None:
        """ Build Panda's DataFrame and format data. """
        self._logger.debug("Construyendo DataFrame a partir de los datos JSON")

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
        self._logger.info("DataFrame construido y ordenado correctamente")

    def _build_base_query_url_params(self) -> str:
        """ Return base query URL parameters.

        Parameters are dependent on the query type:
            https://www.alphavantage.co/documentation/
        URL format:
            https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol=TICKER&outputsize=full&apikey=API_KEY&data_type=json
        """
        self._logger.debug("Generando parámetros base de la URL de consulta")

        return (
            f"function=TIME_SERIES_WEEKLY_ADJUSTED"
            f"&symbol={self._ticker}"
            f"&outputsize=full"
            f"&apikey={self._api_key}"
            )

    @classmethod
    def _build_query_data_key(cls) -> str:
        """ Return data query key. """
        logging.getLogger(__name__).debug(
            "Generando clave de acceso a los datos JSON")

        return "Weekly Adjusted Time Series"

    def _validate_query_data(self) -> None:
        """ Validate query data. """
        self._logger.debug("Validando metadatos de la consulta")

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
        self._logger.info("Solicitando precios semanales")
        self._logger.debug(
            f"Parámetros recibidos: from_date={from_date}, to_date={to_date}")

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
            self._logger.warning("Tipo incorrecto en parámetros de fecha")
            raise FinanceClientParamError(
                "Las fechas deben ser objetos datetime.date")

        # 3. Validar orden
        if from_date > to_date:
            self._logger.warning("from_date > to_date: parámetro inválido")
            raise FinanceClientParamError(
                "from_date no puede ser posterior a to_date")

        # 4. Filtrar
        self._logger.debug("Filtrado de precios completado correctamente")
        return series.loc[from_date:to_date]   # type: ignore

    def weekly_volume(self,
                      from_date: Optional[dt.date] = None,
                      to_date: Optional[dt.date] = None) -> pd.Series:
        """ Return weekly volume from 'from_date' to 'to_date'. """
        self._logger.info("Solicitando volumen semanal")
        self._logger.debug(
            f"Parámetros recibidos: from_date={from_date}, to_date={to_date}")

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
            self._logger.warning("Tipo incorrecto en parámetros de fecha")
            raise FinanceClientParamError(
                "Las fechas deben ser objetos datetime.date"
            )

        # 3. Validar orden
        if from_date > to_date:
            self._logger.warning("from_date > to_date: parámetro inválido")
            raise FinanceClientParamError(
                "from_date no puede ser posterior a to_date"
            )

        # 4. Filtrado correcto
        self._logger.debug("Filtrado de volumen completado correctamente")
        return series.loc[from_date:to_date]  # type: ignore

    def yearly_dividends(self,
                         from_year: Optional[int] = None,
                         to_year: Optional[int] = None) -> pd.Series:
        """ Devuelve el dividendo total anual de from_year y to_year del
        ticket elegido"""
        self._logger.debug(
            "Calculando yearly_dividends(from_year=%s, to_year=%s)", from_year,
            to_year)
        assert self._data_frame is not None

        # validar tipos y rangos de parámetros
        if from_year is not None and not isinstance(from_year, int):
            self._logger.error("from_year no es int: %s", type(from_year))
            raise FinanceClientParamError(
                "from_year debe ser un número entero (int)")

        if to_year is not None and not isinstance(to_year, int):
            self._logger.error("to_year no es int: %s", type(to_year))
            raise FinanceClientParamError(
                "to_year debe ser un número entero (int)")

        if from_year is not None and to_year is not None and from_year > to_year:
            self._logger.error("from_year > to_year (%s > %s)",
                               from_year, to_year)
            raise FinanceClientParamError(
                "from_year no puede ser posterior a to_year")

        self._logger.debug("Extrayendo columna 'dividend' del DataFrame")
        series = self._data_frame['dividend']

        # Agrupamos por el año del índice Datetime y sumamos los dividendos
        self._logger.debug("Agrupando dividendos por año")
        annual_dividends = series.groupby(series.index.year).sum()
        # índice de años

        # Filtramos por el rango de años solicitado
        if from_year is not None:
            self._logger.debug("Filtrando dividendos desde %s", from_year)
            annual_dividends = annual_dividends[
                annual_dividends.index >= from_year]
        if to_year is not None:
            self._logger.debug("Filtrando dividendos hasta %s", to_year)
            annual_dividends = annual_dividends[
                annual_dividends.index <= to_year]

        self._logger.info("Dividendos anuales calculados correctamente")
        return annual_dividends

    def highest_weekly_variation(self,
                                 from_date: Optional[dt.date] = None,
                                 to_date: Optional[dt.date] = None) -> Optional[tuple[dt.date, float, float, float]]:
        """ Devolver (date, high, low, variation) para
        la semana con la mayor variación. """
        self._logger.debug(
            "Calculando highest_weekly_variation(from_date=%s, to_date=%s)",
            from_date, to_date)

        assert self._data_frame is not None

        # Validaciones de tipo
        if from_date is not None and not isinstance(from_date, dt.date):
            self._logger.error("from_date no es datetime.date: %s",
                               type(from_date))
            raise FinanceClientParamError(
                "from_date debe ser un objeto datetime.date")

        if to_date is not None and not isinstance(to_date, dt.date):
            self._logger.error("to_date no es datetime.date: %s",
                               type(to_date))
            raise FinanceClientParamError(
                "to_date debe ser un objeto datetime.date")

        # Validaciones de rango
        if from_date is not None and to_date is not None:
            if from_date > to_date:
                self._logger.error("from_date > to_date (%s > %s)",
                                   from_date, to_date)
                raise FinanceClientParamError(
                    "from_date no puede ser posterior a to_date")

        # Copiamos el dataframe en una copia para no modificarlo
        df_recortado = self._data_frame

        # Aplicamos el filtro de fechas
        if from_date is not None:
            self._logger.debug("Filtrando desde fecha %s", from_date)
            df_recortado = df_recortado[df_recortado.index.date >= from_date]

        if to_date is not None:
            self._logger.debug("Filtrando hasta fecha %s", to_date)
            df_recortado = df_recortado[df_recortado.index.date <= to_date]

        # Si con el rango de fechas vacía el DataFrame,
        # devolvemos None de forma segura
        if df_recortado.empty:
            self._logger.warning("No hay datos en el rango solicitado")
            return None

        # Calculamos la variación (high - low) para todas las filas filtradas
        self._logger.debug("Calculando variación semanal (high - low)")
        variacion = df_recortado['high'] - df_recortado['low']

        # Encontramos la fecha (idmax) donde la variación es la más alta
        fecha_max_var = variacion.idxmax()

        # Extraemos valores para construir la tupla
        fila_max = df_recortado.loc[fecha_max_var]

        high_val = float(fila_max['high'])
        low_val = float(fila_max['low'])
        var_val = float(high_val - low_val)

        # Convertimos el índice DatetimeIndex de Pandas a un objeto
        # datetime.date de python
        fecha_nativa = fecha_max_var.date()

        self._logger.info("Máxima variación encontrada: "
                          "fecha=%s, high=%.2f, low=%.2f, var=%.2f",
                          fecha_nativa, high_val, low_val, var_val)
        return (fecha_nativa, high_val, low_val, var_val)
