"""
Clases de excepción para el subpaquete `teii.finance`.

Incluye excepciones base y especializadas para errores relacionados con
la API financiera, claves inválidas, datos corruptos, errores de E/S y
parámetros incorrectos.
"""


class FinanceClientError(Exception):
    """
    Excepción base para todos los errores del cliente financiero.

    Se utiliza como clase raíz para agrupar todas las excepciones
    específicas del módulo `finance`.

    https://www.loggly.com/blog/exceptional-logging-of-exceptions-in-python/
    (Transformer Pattern)
    """

    pass


class FinanceClientInvalidAPIKey(FinanceClientError):
    """
    Error debido a una clave API inválida o ausente.

    Se lanza cuando la clave proporcionada no existe, no es una cadena
    o no está configurada correctamente en el entorno.
    """

    pass


class FinanceClientAPIError(FinanceClientError):
    """
    Error de acceso a la API financiera.

    Se lanza cuando la petición HTTP falla, devuelve un código de estado
    inesperado o no se puede establecer conexión con el servidor.
    """

    pass


class FinanceClientInvalidData(FinanceClientError):
    """
    Datos inválidos o incompletos devueltos por la API.

    Se lanza cuando el JSON recibido no contiene los campos esperados
    o su estructura no coincide con el formato documentado.
    """

    pass


class FinanceClientIOError(FinanceClientError):
    """
    Error de entrada/salida al leer o escribir datos.

    Se lanza cuando no es posible escribir un archivo CSV o acceder a
    un recurso local.
    """

    pass


# EJERCICIO 'PRICE'
class FinanceClientParamError(FinanceClientError):
    """
    Error en los parámetros proporcionados al cliente.

    Se lanza cuando los argumentos de fecha, año o cualquier parámetro
    de filtrado no cumplen los requisitos esperados.
    """
    pass
