import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import requests
    import json
    import os
    import altair as alt

    return alt, json, mo, pd, requests


@app.cell
def _(mo):

    # Título
    mo.md("""
    # **Panel Pokemon Reactivo con Marimo**
    **Asignatura:** Tecnologías Específicas en Ingeniería Informática <br>
    **Autoras:** <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    Ana Luo Sánchez Botella <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    María Isabel Pérez Lisón
    """)# <br> para saltar a la línea siguiente
    return


@app.cell
def _(mo):
    # Creamos un interruptor (Switch) booleano para elegir el origen de los datos
    modo_api = mo.ui.switch(label="Conectar a la PokéAPI en vivo (Por defecto: Fichero Local)", value=False)

    # Creamos un menú desplegable (Dropdown) con los tipos de nuestros Pokémon para el filtrado
    tipo_selector = mo.ui.dropdown(
        options=["Todos", "electric", "grass", "fire", "poison", "psychic", "water", "normal"],
        value="Todos",
        label="Filtrar por Elemento:"
    )
    return modo_api, tipo_selector


@app.cell
def _(mo, modo_api, tipo_selector):

    # Renderizamos visualmente ambos controles en paralelo dentro del navegador web
    mo.hstack([tipo_selector, modo_api], justify="start")
    return


@app.cell
def _(json, mo, modo_api, requests):
    # Si el switch está activo (True), consumimos la API externa vía HTTP requests.
    # Si está inactivo (False), cargamos el fichero local de respaldo 'pokemon_backup.json'.
    if modo_api.value:
        lista_pokemon_datos = []
        # Lista de vuestros 10 elegidos con sus nombres oficiales en inglés
        nombres_api = ["pikachu", "bulbasaur", "charizard", "arbok", "mewtwo", "slowpoke", "ponyta", "snorlax", "squirtle", "magikarp"]

        try:
            # Hacemos las peticiones HTTP en bucle para recolectar las estadísticas reales
            for nombre in nombres_api:
                res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{nombre}", timeout=3)
                json_pk = res.json()

                # Procesamos el JSON nativo de la API buscando las estadísticas base específicas (base_stat)
                hp = next(s["base_stat"] for s in json_pk["stats"] if s["stat"]["name"] == "hp")
                attack = next(s["base_stat"] for s in json_pk["stats"] if s["stat"]["name"] == "attack")
                defense = next(s["base_stat"] for s in json_pk["stats"] if s["stat"]["name"] == "defense")
                tipo = json_pk["types"][0]["type"]["name"]

                # Construimos un diccionario idéntico al del backup local
                lista_pokemon_datos.append({
                    "name": json_pk["name"],
                    "height": json_pk["height"],
                    "weight": json_pk["weight"],
                    "hp": hp,
                    "attack": attack,
                    "defense": defense,
                    "type": tipo
                })

            datos_finales = {"results": lista_pokemon_datos}
            msg_estado = "**Conectado con éxito a la PokéAPI original en tiempo real por HTTP**"

        except Exception as e:
            # Mecanismo para que si la red falla, se usa el JSON local
            with open("data/pokemon_backup.json", "r", encoding="utf-8") as f:
                datos_finales = json.load(f)
            msg_estado = f"**Error en la API externa ({e}). Activado el protocolo local de respaldo.**"
    else:
        # Carga por defecto del archivo local de forma local
        with open("data/pokemon_backup.json", "r", encoding="utf-8") as f:
            datos_finales = json.load(f)
        msg_estado = "**Fichero local activo ('pokemon_backup.json'). Cumpliendo filosofía de funcionamiento offline.**"

    # Imprimimos el estado dinámico del origen de datos en formato Markdown
    mo.md(msg_estado)
    return (datos_finales,)


@app.cell
def _(datos_finales, pd, tipo_selector):
    # Transformamos la estructura de diccionario JSON a un objeto DataFrame bidimensional de Pandas
    df_raw = pd.DataFrame(datos_finales["results"])

    # Para que quede mejor modificamos la serie de nombres con formato de la primera mayúscula
    df_raw["name"] = df_raw["name"].str.capitalize()

    # Condicionamos las filas basándonos en el estado del desplegable 'tipo_selector.value'
    if tipo_selector.value == "Todos":
        df_filtrado = df_raw
    else:
        df_filtrado = df_raw[df_raw["type"] == tipo_selector.value]

    # Renombramos las etiquetas técnicas de las columnas para la interfaz de usuario
    df_tabla = df_filtrado.rename(columns={
        "name": "Nombre Pokémon",
        "height": "Altura (dm)",
        "weight": "Peso (100g)",
        "hp": "Vida (HP)",
        "attack": "Ataque Base",
        "defense": "Defensa Base",
        "type": "Elemento"
    })
    return df_filtrado, df_tabla


@app.cell
def _(alt, df_filtrado, df_tabla, mo):

    mo.md("### Base de Datos de Características")
    # mo.ui.table permite ordenar interactivamente las filas clicando en las cabeceras
    mo.ui.table(df_tabla)

    mo.md("### Gráfica de Dispersión Interactiva (Ataque vs Defensa)")

    # Construimos una gráfica de dispersión cuantitativa utilizando Altair
    grafico = alt.Chart(df_filtrado).mark_circle(size=180, opacity=0.85).encode(
        x=alt.X('attack:Q', title='Potencial de Ataque Base'),  # Variable cuantitativa en eje X
        y=alt.Y('defense:Q', title='Potencial de Defensa Base'),  # Variable cuantitativa en eje Y
        color=alt.Color('type:N', title='Elemento'),  # Codificación de color nominal basada en el tipo
        tooltip=[  # Configuración del menú flotante de datos interactivos al pasar el ratón (Tooltip)
            alt.Tooltip('name:N', title='Pokémon'),
            alt.Tooltip('type:N', title='Tipo'),
            alt.Tooltip('hp:Q', title='Vida (HP)'),
            alt.Tooltip('attack:Q', title='Ataque'),
            alt.Tooltip('defense:Q', title='Defensa')
        ]
    ).properties(
        width=600,
        height=350
    ).interactive() # .interactive() habilita el zoom y arrastre con el ratón en la web

    # Renderizamos la gráfica exportándola como HTML compatible con la celda de Marimo
    mo.as_html(grafico)
    return


@app.cell
def _(df_tabla, mo):
    mo.md("### Base de Datos Analítica")
    # # mo.ui.table renderiza el DataFrame procesado permitiendo ordenación y filtrado web interactivo haciendo clic
    mo.ui.table(df_tabla)
    return


if __name__ == "__main__":
    app.run()
