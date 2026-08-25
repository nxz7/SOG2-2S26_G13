# Documentación del Agente Conversacional de Análisis de Ventas

## 1. Descripción general

Este proyecto incorpora un agente conversacional para consultar los resultados del análisis de ventas mediante lenguaje natural.

El agente integra **Google ADK**, **Gemini** y un **MCP Server** propio. La interfaz final se implementó con **Streamlit**, de modo que el usuario puede consultar estadísticas, tendencias, segmentaciones, correlaciones y visualizaciones sin ejecutar manualmente consultas SQL o scripts de Python.

El agente no sustituye los cálculos estadísticos realizados por el equipo. Su función es interpretar la pregunta del usuario, seleccionar la herramienta adecuada, recuperar resultados calculados a partir de los datos del proyecto y presentarlos de forma comprensible.

---

## 2. Objetivo

El objetivo del agente es proporcionar una capa de consulta sobre los análisis desarrollados durante la práctica, permitiendo responder preguntas como:

- ¿Cuál fue el mes con mayor facturación?
- ¿Cuál fue el navegador web más utilizado?
- ¿Qué grupo de edad presenta la venta total promedio más alta?
- ¿Existe relación entre la edad y la venta total?
- ¿Existe relación entre el género y el método de pago?
- ¿Cómo cambia el comportamiento de compra según el uso de boletín y vale?
- ¿Qué visualización se utilizó para un análisis determinado?

Además, la interfaz final permite mostrar las gráficas directamente dentro del chat.

---

## 3. Arquitectura

```mermaid
flowchart TD
    A[Usuario] --> B[Interfaz Streamlit]
    B --> C[Google ADK]
    C --> D[Gemini]
    D --> E[MCP Toolset]
    E --> F[MCP Server]

    F --> G[(PostgreSQL)]
    F --> H[Dataset y análisis estadísticos]
    F --> I[Visualizaciones PNG]

    G --> F
    H --> F
    I --> F

    F --> E
    E --> D
    D --> C
    C --> B
    B --> A
```

### Flujo de una consulta

1. El usuario escribe una pregunta en Streamlit.
2. La pregunta se envía al agente creado con Google ADK.
3. Gemini interpreta la intención de la consulta.
4. El agente selecciona la herramienta disponible mediante MCP.
5. La herramienta obtiene los datos o resultados correspondientes.
6. Gemini organiza e interpreta la información recibida.
7. Streamlit presenta la respuesta al usuario.
8. Si la respuesta corresponde a una visualización, la imagen se muestra directamente dentro del chat.

---

## 4. Componentes principales

### `agente/agent.py`

Contiene la configuración principal del agente de Google ADK.

Responsabilidades:

- definir el agente raíz;
- configurar el modelo de Gemini;
- definir las instrucciones del agente;
- conectar el agente con el `McpToolset`;
- exponer las herramientas disponibles al modelo.

El modelo utilizado se configura mediante la variable de entorno:

```text
GEMINI_MODEL
```

Esto permite cambiar el modelo sin modificar directamente la lógica principal del agente.

### `agente/__init__.py`

Permite que Google ADK cargue correctamente el agente definido dentro del paquete `agente`.

### `mcp_server.py`

Implementa el servidor MCP utilizando FastMCP.

Este archivo expone las herramientas que el agente puede utilizar para consultar resultados de:

- estadísticas descriptivas;
- tendencias de ventas;
- navegadores;
- ventas en efectivo;
- boletines y vales;
- segmentación por edad;
- comparación por género;
- correlaciones;
- visualizaciones.

### `chat_app.py`

Implementa la interfaz final con Streamlit.

Responsabilidades:

- crear y mantener la sesión del usuario;
- ejecutar el agente mediante `Runner` de Google ADK;
- conservar el historial de conversación;
- mostrar las respuestas del agente;
- detectar visualizaciones mencionadas por el agente;
- presentar imágenes mediante `st.image()`;
- mantener un único `event_loop` durante la sesión para evitar problemas en la comunicación asíncrona con ADK/MCP.

### `graficos/`

Contiene las visualizaciones generadas durante los análisis realizados por el equipo.

Entre las imágenes utilizadas por el agente se encuentran:

- `3a_ranking_ventas_mes.png`
- `3b_preferencia_navegadores.png`
- `3d_boletines_vales_mes.png`
- `4a_edad_venta.png`
- `4b_genero_compra.png`
- `4c_barras_boletin_vale.png`
- `5c_boletin_vale.png`

### `pruebas/`

Contiene las capturas utilizadas como evidencia de las pruebas funcionales del agente.

---

## 5. Variables de entorno

El proyecto utiliza un archivo `.env` para almacenar configuración sensible.

Ejemplo de estructura:

```env
DATABASE_URL=postgresql://usuario:password@host:puerto/base_datos
GOOGLE_API_KEY=TU_CLAVE_DE_GEMINI
GEMINI_MODEL=nombre-del-modelo
```

> El archivo `.env` no debe almacenarse en el repositorio. Debe permanecer incluido en `.gitignore`.

Variables utilizadas:

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL. |
| `GOOGLE_API_KEY` | Clave utilizada para acceder a Gemini. |
| `GEMINI_MODEL` | Modelo utilizado por el agente. |

---

## 6. Instalación

Desde la raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
```

Para comprobar la versión de Python:

```powershell
python --version
```

Para comprobar que Google ADK está instalado:

```powershell
python -m pip show google-adk
```

Para comprobar MCP:

```powershell
python -m pip show mcp
```

---

## 7. Ejecución

### Interfaz final con Streamlit

Desde la raíz del proyecto:

```powershell
python -m streamlit run chat_app.py
```

Streamlit abrirá normalmente la aplicación en:

```text
http://localhost:8501
```

### Interfaz de desarrollo de Google ADK

También es posible probar el agente desde la interfaz de desarrollo de Google ADK:

```powershell
python -m google.adk.cli web --no-reload
```

La interfaz estará disponible normalmente en:

```text
http://127.0.0.1:8000
```

La interfaz de ADK fue utilizada durante el desarrollo para observar las herramientas seleccionadas por el agente y validar la comunicación con MCP.

---

## 8. Herramientas MCP disponibles

Las herramientas registradas en la versión final del proyecto incluyen:

| Herramienta | Propósito |
|---|---|
| `analizar_estadisticas_basicas` | Obtiene estadísticas descriptivas como media, mediana, moda, desviación, mínimo y máximo. |
| `obtener_estadisticas_monto_compra` | Obtiene estadísticas centrales del monto de compra. |
| `obtener_ventas_por_mes` | Recupera facturación y cantidad de transacciones por mes. |
| `obtener_navegadores` | Analiza la utilización de tienda física y navegadores web. |
| `obtener_ventas_efectivo` | Obtiene cantidad y monto de las compras pagadas en efectivo. |
| `obtener_boletines_vales_por_mes` | Analiza el uso mensual de boletines y vales. |
| `obtener_segmentacion_edad` | Obtiene resultados por grupos de edad. |
| `obtener_segmentacion_boletin_vale` | Segmenta clientes según recepción de boletín y uso de vale. |
| `obtener_comparacion_genero` | Compara el comportamiento de compra entre géneros. |
| `obtener_correlacion_edad_venta` | Devuelve Pearson, Spearman y resultados relacionados con edad y venta total. |
| `obtener_correlacion_genero_pago` | Devuelve Chi-cuadrado y V de Cramer para género y método de pago. |
| `obtener_correlacion_boletin_vale` | Evalúa estadísticamente la relación entre boletín y vale. |
| `analizar_boletin_vale` | Integra segmentación y relación estadística entre boletín y vale. |
| `obtener_visualizaciones` | Identifica las gráficas disponibles y proporciona su información al agente. |

---

## 9. Integración con los análisis del equipo

El agente fue diseñado para reutilizar el trabajo realizado en los puntos anteriores de la práctica.

Para los análisis de tendencias, diferentes herramientas consultan la base de datos PostgreSQL utilizada por el proyecto.

Para estadísticas, segmentaciones y correlaciones se reutiliza la misma metodología aplicada durante los análisis originales, de modo que las respuestas del agente sean consistentes con los resultados previamente calculados por el equipo.

Esta separación es importante porque:

- Gemini interpreta la pregunta y redacta la respuesta;
- las herramientas MCP entregan los valores obtenidos a partir de los datos;
- el modelo no debe inventar los resultados estadísticos.

---

## 10. Visualizaciones dentro del chat

El proyecto requiere que el usuario pueda observar las gráficas directamente desde la interfaz conversacional.

La herramienta `obtener_visualizaciones` mantiene información sobre las imágenes generadas previamente, incluyendo:

- nombre del archivo;
- punto de la práctica;
- título;
- descripción;
- hallazgo principal;
- ruta de la imagen.

Cuando el agente menciona una imagen disponible, `chat_app.py` compara la respuesta contra las rutas conocidas dentro de `graficos/`.

Si el archivo existe, Streamlit lo muestra mediante:

```python
st.image(imagen, use_container_width=True)
```

Ejemplo de consulta:

> Muéstrame la visualización utilizada para analizar el comportamiento de compra por edad.

El agente identifica `4a_edad_venta.png`, explica su contenido y Streamlit muestra la gráfica directamente dentro de la conversación.

---

## 11. Ejemplos de consultas

### Estadísticas descriptivas

```text
¿Cuáles son la media, mediana y moda de Edad y Venta_total?
```

### Tendencias

```text
¿Cuál fue el mes con mayor facturación y cuál tuvo la menor?
```

### Navegadores

```text
Considerando únicamente los navegadores web, ¿cuál fue el navegador más utilizado y cuál fue el menos utilizado?
```

### Segmentación

```text
¿Qué grupo de edad tiene la venta total promedio más alta?
```

### Boletín y vale

```text
Compara el comportamiento de compra de los clientes según si reciben boletín y utilizan vale.
```

### Correlación edad y venta

```text
¿Existe relación entre la edad del cliente y la venta total? Reporta Pearson y Spearman.
```

### Género y método de pago

```text
¿Existe una relación estadísticamente significativa entre el género y el método de pago? Usa chi-cuadrado y reporta el p-valor.
```

### Visualización

```text
Muéstrame la visualización utilizada para analizar el comportamiento de compra por edad.
```

---

## 12. Validación de herramientas

### Verificar herramientas registradas en FastMCP

```powershell
python -c "import mcp_server; print([t.name for t in mcp_server.mcp._tool_manager.list_tools()])"
```

### Verificar herramientas visibles para Google ADK

```powershell
python -c "import asyncio; from agente.agent import root_agent; tools=asyncio.run(root_agent.tools[0].get_tools()); print([t.name for t in tools])"
```

Ambas listas deben contener las herramientas que el agente necesita utilizar.

### Verificar el modelo configurado

```powershell
python -c "from agente.agent import root_agent; print(root_agent.model)"
```

---

## 13. Pruebas realizadas

Se realizaron pruebas funcionales para comprobar que el agente pudiera consultar resultados correspondientes a los puntos 2 al 6 de la práctica.

| Prueba | Consulta evaluada | Resultado esperado |
|---|---|---|
| Estadísticas | Media, mediana y moda | Recuperar valores del análisis exploratorio. |
| Ventas mensuales | Mayor y menor facturación | Marzo como mayor y noviembre como menor. |
| Navegadores | Mayor y menor navegador web | Navegador 1 y Navegador 4. |
| Segmentación por edad | Mayor venta total promedio | Grupo de 26 a 35 años. |
| Boletín y vale | Comparación de los cuatro grupos | Recuperar segmentación y análisis estadístico. |
| Edad vs. venta total | Pearson y Spearman | Presentar coeficientes e interpretación. |
| Género vs. método de pago | Chi-cuadrado y p-valor | Presentar prueba e interpretación. |
| Visualización | Mostrar gráfica de edad | Mostrar el PNG directamente dentro del chat. |

Las capturas de estas pruebas se encuentran almacenadas en la carpeta `pruebas/`.

---

## 14. Problemas encontrados y soluciones

### 14.1. Comando `adk` no reconocido

En algunos entornos Windows el comando:

```powershell
adk web
```

puede no encontrarse directamente en `PATH`.

Se utilizó:

```powershell
python -m google.adk.cli web --no-reload
```

### 14.2. Modelo de Gemini no disponible

Durante el desarrollo algunos modelos devolvieron errores de disponibilidad.

Solución:

- consultar los modelos disponibles mediante la API;
- utilizar `GEMINI_MODEL` como variable de entorno;
- seleccionar un modelo disponible sin modificar la lógica principal.

### 14.3. Error `429 RESOURCE_EXHAUSTED`

Este error indica que se alcanzó un límite de cuota o solicitudes del modelo.

No corresponde a un error de las herramientas MCP. En estos casos se debe esperar el período indicado por el servicio, reducir la frecuencia de pruebas o utilizar un modelo/cuota disponible.

### 14.4. `Tool not found`

Durante algunas pruebas el modelo intentó utilizar nombres de herramientas inexistentes o variantes de herramientas reales.

Para diagnosticarlo se compararon:

- las herramientas registradas en FastMCP;
- las herramientas visibles desde `McpToolset`;
- los nombres solicitados por Gemini.

También se simplificaron algunas operaciones relacionadas, como la herramienta integrada `analizar_boletin_vale`.

### 14.5. Comunicación asíncrona en Streamlit

Durante la integración con Streamlit se presentaron problemas al reutilizar conexiones asíncronas.

La solución fue mantener un único ciclo de eventos durante la sesión:

```python
if "event_loop" not in st.session_state:
    st.session_state.event_loop = asyncio.new_event_loop()
```

Las llamadas se ejecutan utilizando ese mismo ciclo:

```python
def ejecutar_async(corutina):
    loop = st.session_state.event_loop
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(corutina)
```

### 14.6. Visualizaciones no mostradas en ADK Dev UI

La interfaz de desarrollo de ADK permitió probar correctamente el agente y las herramientas, pero la presentación directa de las imágenes requería mayor control sobre la interfaz.

Por esta razón se utilizó Streamlit como interfaz final.

---

## 15. Seguridad

Las credenciales no deben escribirse directamente dentro de los archivos Python.

El archivo `.env` debe mantenerse fuera del repositorio mediante `.gitignore`.

Ejemplo recomendado de `.gitignore`:

```gitignore
__pycache__/
*.pyc
.env
.adk/
```

Si una clave API o una contraseña fue publicada previamente en un repositorio, debe considerarse comprometida y reemplazarse.

---

## 16. Limitaciones actuales

El agente depende de los análisis y herramientas actualmente implementados.

Por lo tanto:

- no puede responder correctamente sobre variables que no existen en el dataset;
- no debe inferir categorías inexistentes, como ventas contra entrega si no están representadas de forma independiente en los datos;
- las visualizaciones disponibles son las generadas previamente por el equipo;
- la disponibilidad del modelo depende de la cuota y del servicio de Gemini;
- incorporar nuevos análisis requiere agregar o actualizar herramientas en el MCP Server.

---

## 17. Mantenimiento y ampliación

Para agregar un nuevo análisis al agente se recomienda seguir este proceso:

1. Implementar y validar primero el análisis con los datos reales.
2. Crear una herramienta nueva en `mcp_server.py` mediante `@mcp.tool()`.
3. Utilizar un nombre descriptivo y diferente a las herramientas existentes.
4. Escribir un docstring que explique claramente qué devuelve la herramienta.
5. Verificar que FastMCP registre la herramienta.
6. Verificar que Google ADK pueda verla mediante `McpToolset`.
7. Actualizar las instrucciones del agente si es necesario.
8. Probar la herramienta desde ADK Dev UI.
9. Probar la misma consulta desde Streamlit.
10. Documentar la nueva funcionalidad y su evidencia.

Para agregar una nueva visualización:

1. guardar el archivo dentro de `graficos/`;
2. registrarlo en la estructura de visualizaciones utilizada por el MCP Server;
3. agregar su ruta al diccionario `GRAFICOS` de `chat_app.py`;
4. probar que el agente mencione correctamente el nombre del archivo;
5. comprobar que Streamlit pueda mostrarlo.

---

## 18. Estructura relacionada con el agente

```text
SOG2-2S26_G13/
│
├── agente/
│   ├── __init__.py
│   ├── agent.py
│   └── icono.png
│
├── graficos/
│   ├── 3a_ranking_ventas_mes.png
│   ├── 3b_preferencia_navegadores.png
│   ├── 3d_boletines_vales_mes.png
│   ├── 4a_edad_venta.png
│   ├── 4b_genero_compra.png
│   ├── 4c_barras_boletin_vale.png
│   └── 5c_boletin_vale.png
│
├── pruebas/
│   └── evidencias de pruebas del chat
│
├── .env
├── .gitignore
├── chat_app.py
├── mcp_server.py
└── requirements.txt
```

---

## 19. Conclusión

El agente conversacional integra los diferentes análisis del proyecto dentro de una sola interfaz de consulta.

Google ADK administra el agente, Gemini interpreta las preguntas y genera las explicaciones, mientras que el MCP Server proporciona acceso a los resultados calculados a partir de los datos reales del proyecto.

La interfaz de Streamlit permite consultar esta información mediante lenguaje natural y mostrar las visualizaciones directamente dentro de la conversación.

La principal ventaja de esta arquitectura es que separa los cálculos del modelo de lenguaje: el agente utiliza herramientas para obtener los valores y posteriormente los presenta al usuario, reduciendo el riesgo de depender únicamente de información generada por la IA.
