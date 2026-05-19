"""
Cliente especializado para series temporales semanales ajustadas (AlphaVantage)

Este módulo implementa `TimeSeriesFinanceClient`, una clase derivada de
`FinanceClient` que consulta la función `TIME_SERIES_WEEKLY_ADJUSTED` de
AlphaVantage, valida los metadatos, construye un DataFrame ordenado y
proporciona métodos para obtener precios, volumen, dividendos y variaciones
semanales.

Notes
-----
Los datos siguen el formato documentado en:
https://www.alphavantage.co/documentation/
"""


import datetime as dt
import logging
from typing import Optional, Union

import pandas as pd

from teii.finance import (FinanceClient, FinanceClientInvalidData,
                          FinanceClientParamError)


class TimeSeriesFinanceClient(FinanceClient):
    """
    Cliente para series temporales semanales ajustadas de AlphaVantage.

    Gestiona la construcción de la URL de consulta, la validación de metadatos,
    la conversión del JSON recibido a un `pandas.DataFrame` y la exposición de
    métodos de análisis como precios, volumen, dividendos y variación semanal.

    Parameters
    ----------
    ticker : str
        Símbolo bursátil (por ejemplo, 'NVDA').
    api_key : str, optional
        Clave API para AlphaVantage. Si no se proporciona, se intenta obtener
        de la variable de entorno `TEII_FINANCE_API_KEY`.
    logging_level : int or str, optional
        Nivel de logging para el cliente.

    Attributes
    ----------
    _data_frame : pandas.DataFrame
        DataFrame con los datos semanales ajustados, ordenados por fecha.
    _json_metadata : dict
        Metadatos devueltos por la API.
    _json_data : dict
        Datos semanales ajustados devueltos por la API.

    Raises
    ------
    FinanceClientInvalidData
        Si los metadatos no contienen el símbolo esperado.
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
        """
        Construye el DataFrame de pandas a partir del JSON recibido.

        Convierte los campos numéricos a sus tipos correctos, renombra las
        columnas según `_data_field2name_type`, convierte el índice a fechas
        y ordena el DataFrame cronológicamente.

        Raises
        ------
        FinanceClientInvalidData
            Si los datos no pueden convertirse correctamente en un DataFrame.
        """
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
        """
        Construye los parámetros base de la consulta para AlphaVantage.

        Returns
        -------
        str
            Cadena con los parámetros necesarios para la función
            `TIME_SERIES_WEEKLY_ADJUSTED`.
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
        """
        Devuelve la clave del JSON donde se encuentran los datos semanales.

        Returns
        -------
        str
            Nombre del campo JSON que contiene los datos de la serie temporal.
        """
        logging.getLogger(__name__).debug(
            "Generando clave de acceso a los datos JSON")

        return "Weekly Adjusted Time Series"

    def _validate_query_data(self) -> None:
        """
        Valida que los metadatos de la API coinciden con el ticker solicitado.

        Raises
        ------
        FinanceClientInvalidData
            Si el campo '2. Symbol' no coincide con el ticker del cliente.
        """

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
        """
        Devuelve la serie de precios ajustados semanales.

        Parameters
        ----------
        from_date : datetime.date, optional
            Fecha inicial del rango.
        to_date : datetime.date, optional
            Fecha final del rango.

        Returns
        -------
        pandas.Series
            Serie temporal con precios ajustados ('aclose').

        Raises
        ------
        FinanceClientParamError
            Si las fechas no son válidas o si from_date > to_date.

        Examples
        --------
        >>> client.weekly_price(date(2025, 1, 1), date(2025, 12, 31))
        """
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
        """
        Devuelve la serie de volumen semanal.

        Parameters
        ----------
        from_date : datetime.date, optional
            Fecha inicial del rango.
        to_date : datetime.date, optional
            Fecha final del rango.

        Returns
        -------
        pandas.Series
            Serie temporal con el volumen semanal.

        Raises
        ------
        FinanceClientParamError
            Si las fechas no son válidas o si from_date > to_date.
        """
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
        """
        Calcula los dividendos anuales totales en un rango de años.

        Parameters
        ----------
        from_year : int, optional
            Año inicial del rango.
        to_year : int, optional
            Año final del rango.

        Returns
        -------
        pandas.Series
            Serie con dividendos totales por año.

        Raises
        ------
        FinanceClientParamError
            Si los años no son enteros o si from_year > to_year.
        """
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
        """
        Devuelve la semana con mayor variación (high - low).

        Parameters
        ----------
        from_date : datetime.date, optional
            Fecha inicial del rango.
        to_date : datetime.date, optional
            Fecha final del rango.

        Returns
        -------
        tuple or None
            (fecha, high, low, variación) o None si no hay datos.

        Raises
        ------
        FinanceClientParamError
            Si las fechas no son válidas o si from_date > to_date.
        """
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
