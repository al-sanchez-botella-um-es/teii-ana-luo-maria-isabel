"""
Subpaquete `teii.finance`.

Proporciona clases y excepciones para acceder a datos financieros desde
AlphaVantage, procesarlos y convertirlos en estructuras pandas listas
para análisis.
"""


from .exception import (FinanceClientAPIError, FinanceClientInvalidAPIKey,
                        FinanceClientInvalidData, FinanceClientIOError,
                        FinanceClientParamError)

from .finance import FinanceClient
from .timeseries import TimeSeriesFinanceClient

__all__ = ('FinanceClientInvalidAPIKey',
           'FinanceClientAPIError',
           'FinanceClientInvalidData',
           'FinanceClientIOError',
           'FinanceClient',
           'TimeSeriesFinanceClient',
           'FinanceClientParamError')
