"""
Funciones de saludo y despedida para demostración del paquete `teii`.

Este módulo contiene funciones simples utilizadas en ejemplos y pruebas
para ilustrar el funcionamiento básico del paquete.
"""


def greeting(name: str) -> str:
    """
    Genera un mensaje de saludo personalizado.

    Parameters
    ----------
    name : str
        Nombre de la persona a saludar.

    Returns
    -------
    str
        Mensaje de saludo.

    Examples
    --------
    >>> greeting("Bob")
    'Hello Bob'
    """
    return f"Hello {name}"


def farewell(name):
    """
    Genera un mensaje de despedida personalizado.

    Parameters
    ----------
    name : str
        Nombre de la persona a despedir.

    Returns
    -------
    str
        Mensaje de despedida.

    Examples
    --------
    >>> farewell("Bob")
    'Bye Bob'
    """
    return f"Bye {name}"


greeting("Bob")
greeting(b'Alice')
greeting(3)

farewell("Bob")
farewell(b'Alice')
farewell(3)
