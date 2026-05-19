"""
Ejemplo de uso del paquete `teii.finance`.

Este módulo muestra cómo configurar el sistema de logging, crear un cliente
financiero, obtener precios semanales filtrados por fecha y generar una
gráfica con matplotlib.
"""


import logging

import matplotlib.pyplot as plt

import teii.finance as tf

import datetime as dt

# EJERCICIO 'LOGGING':
"""logging.basicConfig(
    filename="example.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)"""
# Cambiando el nivel, cambia el contenido del example.log
logger = logging.getLogger("example")
logger.setLevel(logging.DEBUG)   # Nivel para example.py

handler = logging.FileHandler("example.log")
handler.setLevel(logging.DEBUG)  # Nivel del handler

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)

# para teii.finance
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(handler)


def setup_logging(logging_level):
    """
    Configura y devuelve un logger para el ejemplo.

    Parameters
    ----------
    logging_level : int
        Nivel de logging (por ejemplo, logging.DEBUG).

    Returns
    -------
    logging.Logger
        Logger configurado para el módulo.
    """

    # Configura logging para enviar la salida a un archivo

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)
    logger.info("Logger creado")

    return logger


def plot(pandas_series, ticker, logger):
    """
    Dibuja una gráfica a partir de una serie temporal de pandas.

    Parameters
    ----------
    pandas_series : pandas.Series
        Serie temporal con los valores a representar.
    ticker : str
        Símbolo bursátil asociado a la serie.
    logger : logging.Logger
        Logger para registrar el proceso de dibujo.
    """

    logger.info("Dibujando gráfica...")

    pandas_series.plot(xlabel='Fecha', ylabel='Precio en USD',
                       title=f"Evolución del Precio de {ticker}")
    plt.show()  # ¡Necesario para que se muestre la gráfica en una ventana!


def main():
    """
    Ejecuta un ejemplo completo de uso del cliente financiero.

    Realiza:
    - Configuración del logger
    - Creación del cliente financiero
    - Obtención de precios semanales filtrados al año 2026
    - Representación gráfica de los datos

    Notes
    -----
    Este ejemplo utiliza una API key ficticia. Para un uso real, debe
    configurarse una clave válida desde AlphaVantage.
    """

    # logger = setup_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Inicio")

    # Define ticker y API key
    ticker = 'IBM'
    my_alpha_vantage_api_key = 'api_key_inventada'
    # Sólo funcionará con IBM (para demos)
    # Obtener un API key real de https://www.alphavantage.co/support/#api-key
    # (Pero hay fuertes limitaciones de uso diario, ojo, no más de 1 llamada
    # por segundo
    #  5 llamadas por minuto y 25 llamadas por día),

    # Crea cliente
    try:
        tf_client = tf.TimeSeriesFinanceClient(ticker,
                                               my_alpha_vantage_api_key,
                                               logging_level=logging.DEBUG)
    # Captura y muestra todas las excepciones
    except Exception as e:
        logger.error(f"{e}", exc_info=False)
    # Usa el cliente
    else:
        # EJERCICIO 'PRICE':
        #   Filtra los datos para mostrar únicamente el año 2026
        inicio_2026 = dt.date(2026, 1, 1)
        fin_2026 = dt.date(2026, 12, 31)

        # Genera una serie de Pandas con precio de cierre semanal
        pd_series = tf_client.weekly_price(
            from_date=inicio_2026,
            to_date=fin_2026
        )

        logger.info(pd_series)

        # Dibuja una gráfica a partir de la serie de Pandas
        plot(pd_series, ticker, logger)
    finally:
        logger.info("Fin")


# Es necesario!
# _name_ es un atributo de los módulos de python (el nombre del fichero),
# que se referencia desde la línea de comandos, a la hora de ejecutarlo.


if __name__ == "__main__":
    main()
