import asyncio
import os
import re
import uuid

import streamlit as st

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agente.agent import root_agent


APP_NAME = "agente"
USER_ID = "usuario_streamlit"


# ---------------------------------------------------------
# CONFIGURACIÓN VISUAL
# ---------------------------------------------------------

st.set_page_config(
    page_title="Asistente de Análisis de Ventas",
    page_icon="agente/icono.png",
    layout="centered"
)

st.title("Asistente de Análisis de Ventas") 

st.caption(
    "Consulta estadísticas, tendencias, segmentaciones, "
    "correlaciones y visualizaciones del proyecto."
)


# ---------------------------------------------------------
# GRÁFICOS DISPONIBLES
# ---------------------------------------------------------

GRAFICOS = {
    "3a_ranking_ventas_mes.png":
        "graficos/3a_ranking_ventas_mes.png",

    "3b_preferencia_navegadores.png":
        "graficos/3b_preferencia_navegadores.png",

    "3d_boletines_vales_mes.png":
        "graficos/3d_boletines_vales_mes.png",

    "4a_edad_venta.png":
        "graficos/4a_edad_venta.png",

    "4b_genero_compra.png":
        "graficos/4b_genero_compra.png",

    "4c_barras_boletin_vale.png":
        "graficos/4c_barras_boletin_vale.png",

    "5c_boletin_vale.png":
        "graficos/5c_boletin_vale.png",
}


# ---------------------------------------------------------
# SESIÓN ADK
# ---------------------------------------------------------

if "event_loop" not in st.session_state:
    st.session_state.event_loop = asyncio.new_event_loop()

if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "runner" not in st.session_state:
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=st.session_state.session_service
    )

if "session_created" not in st.session_state:
    st.session_state.session_created = False

if "messages" not in st.session_state:
    st.session_state.messages = []


async def asegurar_sesion():
    if not st.session_state.session_created:

        await st.session_state.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=st.session_state.session_id
        )

        st.session_state.session_created = True


# ---------------------------------------------------------
# LLAMADA AL AGENTE
# ---------------------------------------------------------
def ejecutar_async(corutina):
    """
    Ejecuta todas las llamadas asíncronas de ADK/MCP
    dentro del mismo event loop durante la sesión.
    """
    loop = st.session_state.event_loop
    asyncio.set_event_loop(loop)

    return loop.run_until_complete(corutina)

async def consultar_agente(pregunta: str) -> str:

    await asegurar_sesion()

    mensaje = types.Content(
        role="user",
        parts=[
            types.Part(text=pregunta)
        ]
    )

    eventos = st.session_state.runner.run_async(
        user_id=USER_ID,
        session_id=st.session_state.session_id,
        new_message=mensaje
    )

    respuesta_final = ""

    async for evento in eventos:

        if evento.is_final_response():

            if evento.content and evento.content.parts:

                respuesta_final = "".join(
                    parte.text or ""
                    for parte in evento.content.parts
                )

    return respuesta_final


# ---------------------------------------------------------
# DETECTAR IMÁGENES MENCIONADAS
# ---------------------------------------------------------

def detectar_graficos(texto: str):

    encontrados = []

    for nombre, ruta in GRAFICOS.items():

        if nombre.lower() in texto.lower():

            if os.path.exists(ruta):
                encontrados.append(ruta)

    return encontrados


# ---------------------------------------------------------
# HISTORIAL
# ---------------------------------------------------------

for mensaje in st.session_state.messages:

    with st.chat_message(mensaje["role"]):

        st.markdown(mensaje["content"])

        for imagen in mensaje.get("images", []):
            st.image(imagen, use_container_width=True)


# ---------------------------------------------------------
# CHAT
# ---------------------------------------------------------

pregunta = st.chat_input(
    "Escribe una pregunta sobre los análisis..."
)

if pregunta:

    st.session_state.messages.append({
        "role": "user",
        "content": pregunta,
        "images": []
    })

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):

        with st.spinner("Analizando datos..."):

            try:

                respuesta = ejecutar_async(
                    consultar_agente(pregunta)
                )

                st.markdown(respuesta)

                imagenes = detectar_graficos(respuesta)

                for imagen in imagenes:
                    st.image(
                        imagen,
                        use_container_width=True
                    )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": respuesta,
                    "images": imagenes
                })

            except Exception as error:

                st.error(
                    f"Ocurrió un error al consultar el agente: {error}"
                )

