import os

import pandas as pd
from scipy import stats
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from mcp.server.fastmcp import FastMCP


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

mcp = FastMCP("analisis-ventas")


@mcp.tool()
def obtener_ventas_por_mes() -> list[dict]:
    """
    Obtiene el monto total vendido y la cantidad de transacciones
    realizadas en cada mes.
    """

    query = text("""
        SELECT
            EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes,
            SUM(monto_compra) AS monto_total,
            COUNT(*) AS cantidad_ventas
        FROM compra
        GROUP BY EXTRACT(MONTH FROM fecha_compra)
        ORDER BY mes;
    """)

    with engine.connect() as conexion:
        resultado = conexion.execute(query)

        return [
            {
                "mes": fila.mes,
                "monto_total": float(fila.monto_total),
                "cantidad_ventas": fila.cantidad_ventas
            }
            for fila in resultado
        ]

@mcp.tool()
def obtener_navegadores() -> list[dict]:
    """
    Obtiene la cantidad de transacciones, monto total y porcentaje
    correspondientes a cada canal o navegador.
    """

    query = text("""
        SELECT
            n.id_navegador,
            n.nombre,
            COUNT(*) AS cantidad,
            SUM(c.monto_compra) AS monto_total,
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS porcentaje
        FROM compra c
        JOIN navegador n
            ON c.id_navegador = n.id_navegador
        GROUP BY n.id_navegador, n.nombre
        ORDER BY cantidad DESC;
    """)

    with engine.connect() as conexion:
        resultado = conexion.execute(query)

        return [
            {
                "id_navegador": fila.id_navegador,
                "nombre": fila.nombre,
                "cantidad": fila.cantidad,
                "monto_total": float(fila.monto_total),
                "porcentaje": float(fila.porcentaje)
            }
            for fila in resultado
        ]


@mcp.tool()
def obtener_ventas_efectivo() -> dict:
    """
    Obtiene la cantidad, monto total y porcentaje de ventas
    realizadas mediante efectivo.
    """

    query = text("""
        SELECT
            COUNT(*) AS cantidad_ventas,
            SUM(c.monto_compra) AS monto_total,
            COUNT(*) * 100.0 /
                (SELECT COUNT(*) FROM compra) AS porcentaje
        FROM compra c
        JOIN metodo_pago mp
            ON c.id_metodo_pago = mp.id_metodo_pago
        WHERE LOWER(mp.nombre) = 'efectivo';
    """)

    with engine.connect() as conexion:
        fila = conexion.execute(query).fetchone()

        return {
            "cantidad_ventas": fila.cantidad_ventas,
            "monto_total": float(fila.monto_total),
            "porcentaje": float(fila.porcentaje)
        }


@mcp.tool()
def obtener_boletines_vales_por_mes() -> list[dict]:
    """
    Obtiene el número de boletines y vales utilizados
    durante cada mes del año.
    """

    query = text("""
        SELECT
            EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes,
            SUM(CASE WHEN boletin = 1 THEN 1 ELSE 0 END) AS boletines,
            SUM(CASE WHEN vale = 1 THEN 1 ELSE 0 END) AS vales
        FROM compra
        GROUP BY EXTRACT(MONTH FROM fecha_compra)
        ORDER BY mes;
    """)

    with engine.connect() as conexion:
        resultado = conexion.execute(query)

        return [
            {
                "mes": fila.mes,
                "boletines": fila.boletines,
                "vales": fila.vales
            }
            for fila in resultado
        ]
    
@mcp.tool()
def analizar_estadisticas_basicas() -> dict:
    """
    Obtiene las estadísticas descriptivas utilizadas en el análisis
    exploratorio del equipo para Edad, Venta_total, MontoCompra y Tiempo.

    Calcula:
    - media
    - mediana
    - moda
    - frecuencia de la moda
    - desviación estándar
    - mínimo
    - máximo
    - cantidad de observaciones
    """

    rutas = [
        "resultados/Venta_online_c.csv",
        "Venta_online_c.csv"
    ]

    df = None

    for ruta in rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=";")
            break

    if df is None:
        raise FileNotFoundError(
            "No se encontró Venta_online_c.csv"
        )

    variables = [
        "Edad",
        "Venta_total",
        "MontoCompra",
        "Tiempo"
    ]

    resultado = {}

    for variable in variables:
        serie = df[variable].dropna()

        conteo = serie.value_counts()

        moda = conteo.index[0]
        frecuencia_moda = conteo.iloc[0]

        resultado[variable] = {
            "media": float(serie.mean()),
            "mediana": float(serie.median()),
            "moda": float(moda),
            "frecuencia_moda": int(frecuencia_moda),
            "desviacion_estandar": float(serie.std()),
            "minimo": float(serie.min()),
            "maximo": float(serie.max()),
            "cantidad_observaciones": int(serie.count())
        }

    return resultado


@mcp.tool()
def obtener_estadisticas_monto_compra() -> dict:
    """
    Calcula media, mediana y moda del monto de las compras.
    """

    query = text("""
        SELECT
            AVG(monto_compra) AS media,
            PERCENTILE_CONT(0.5)
                WITHIN GROUP (ORDER BY monto_compra) AS mediana,
            MODE()
                WITHIN GROUP (ORDER BY monto_compra) AS moda,
            MIN(monto_compra) AS minimo,
            MAX(monto_compra) AS maximo,
            COUNT(*) AS cantidad
        FROM compra;
    """)

    with engine.connect() as conexion:
        fila = conexion.execute(query).fetchone()

        return {
            "media": float(fila.media),
            "mediana": float(fila.mediana),
            "moda": float(fila.moda),
            "minimo": float(fila.minimo),
            "maximo": float(fila.maximo),
            "cantidad": fila.cantidad
        }


@mcp.tool()
def obtener_segmentacion_edad() -> list[dict]:
    """
    Analiza los patrones de compra por grupo de edad
    utilizando la misma metodología del análisis original.
    """

    rutas = [
        "resultados/Venta_online_c.csv",
        "Venta_online_c.csv"
    ]

    df = None

    for ruta in rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=";")
            break

    if df is None:
        raise FileNotFoundError(
            "No se encontró el archivo Venta_online_c.csv"
        )

    rangos_edad = [17, 25, 35, 45, 55, 79]

    nombres_rangos = [
        "18-25",
        "26-35",
        "36-45",
        "46-55",
        "56-79"
    ]

    df["GrupoEdad"] = pd.cut(
        df["Edad"],
        bins=rangos_edad,
        labels=nombres_rangos,
        include_lowest=True
    )

    segmento = (
        df.groupby(
            "GrupoEdad",
            observed=True
        )
        .agg(
            clientes=("Id_cliente", "count"),
            venta_promedio=("Venta_total", "mean"),
            compras_promedio=("N_Compras", "mean"),
            monto_promedio=("MontoCompra", "mean")
        )
        .round(2)
        .reset_index()
    )

    return [
        {
            "grupo_edad": str(fila["GrupoEdad"]),
            "clientes": int(fila["clientes"]),
            "venta_total_promedio": float(
                fila["venta_promedio"]
            ),
            "numero_compras_promedio": float(
                fila["compras_promedio"]
            ),
            "monto_compra_promedio": float(
                fila["monto_promedio"]
            )
        }
        for _, fila in segmento.iterrows()
    ]


@mcp.tool()
def obtener_segmentacion_boletin_vale() -> list[dict]:
    """
    Analiza los patrones de compra según recepción de boletín
    y utilización de vale, utilizando la misma metodología
    del análisis original del equipo.
    """

    rutas = [
        "resultados/Venta_online_c.csv",
        "Venta_online_c.csv"
    ]

    df = None

    for ruta in rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=";")
            break

    if df is None:
        raise FileNotFoundError(
            "No se encontró Venta_online_c.csv"
        )

    segmento = (
        df.groupby(["Boletin", "Vale"])
        .agg(
            clientes=("Id_cliente", "count"),
            venta_promedio=("Venta_total", "mean"),
            compras_promedio=("N_Compras", "mean"),
            monto_promedio=("MontoCompra", "mean")
        )
        .round(2)
        .reset_index()
    )

    return [
        {
            "boletin": (
                "Sí" if int(fila["Boletin"]) == 1 else "No"
            ),
            "vale": (
                "Sí" if int(fila["Vale"]) == 1 else "No"
            ),
            "clientes": int(fila["clientes"]),
            "venta_total_promedio": float(
                fila["venta_promedio"]
            ),
            "numero_compras_promedio": float(
                fila["compras_promedio"]
            ),
            "monto_compra_promedio": float(
                fila["monto_promedio"]
            )
        }
        for _, fila in segmento.iterrows()
    ]

    
@mcp.tool()
def obtener_comparacion_genero() -> list[dict]:
    """
    Compara el comportamiento de compra entre géneros.
    """

    query = text("""
        SELECT
            cl.genero,
            COUNT(DISTINCT cl.id_cliente) AS clientes,
            COUNT(co.id_compra) AS compras,
            AVG(co.monto_compra) AS compra_promedio,
            SUM(co.monto_compra) AS monto_total

        FROM cliente cl

        JOIN compra co
            ON cl.id_cliente = co.id_cliente

        GROUP BY cl.genero

        ORDER BY cl.genero;
    """)

    with engine.connect() as conexion:
        resultado = conexion.execute(query)

        return [
            {
                "genero": (
                    "Femenino"
                    if fila.genero == 1
                    else "Masculino"
                ),
                "clientes": fila.clientes,
                "compras": fila.compras,
                "compra_promedio": float(fila.compra_promedio),
                "monto_total": float(fila.monto_total)
            }
            for fila in resultado
        ]
    

@mcp.tool()
def obtener_correlacion_edad_venta() -> dict:
    """
    Analiza la relación entre la edad del cliente y su venta total.

    Calcula:
    - asimetría de edad y venta total
    - correlación de Pearson
    - correlación de Spearman
    - regresión lineal simple
    - R cuadrado
    """

    query = text("""
        SELECT
            cl.id_cliente,
            cl.edad,
            SUM(co.monto_compra) AS venta_total
        FROM cliente cl
        JOIN compra co
            ON cl.id_cliente = co.id_cliente
        GROUP BY cl.id_cliente, cl.edad
        ORDER BY cl.id_cliente;
    """)

    with engine.connect() as conexion:
        df = pd.read_sql(query, conexion)

    skew_venta = df["venta_total"].skew()
    skew_edad = df["edad"].skew()

    pearson_r, pearson_p = stats.pearsonr(
        df["edad"],
        df["venta_total"]
    )

    spearman_r, spearman_p = stats.spearmanr(
        df["edad"],
        df["venta_total"]
    )

    regresion = stats.linregress(
        df["edad"],
        df["venta_total"]
    )

    return {
        "asimetria_venta_total": float(skew_venta),
        "asimetria_edad": float(skew_edad),

        "pearson": {
            "r": float(pearson_r),
            "p_valor": float(pearson_p)
        },

        "spearman": {
            "rho": float(spearman_r),
            "p_valor": float(spearman_p)
        },

        "regresion_lineal": {
            "intercepto": float(regresion.intercept),
            "pendiente": float(regresion.slope),
            "r_cuadrado": float(regresion.rvalue ** 2),
            "p_valor": float(regresion.pvalue)
        },

        "cantidad_clientes": int(len(df))
    }



@mcp.tool()
def obtener_correlacion_genero_pago() -> dict:
    """
    Analiza la relación entre género y método de pago.

    Utiliza:
    - tabla de contingencia
    - porcentajes por género
    - prueba Chi-cuadrado
    - Cramer's V
    """

    query = text("""
        SELECT
            cl.genero,
            mp.nombre AS metodo_pago
        FROM compra co
        JOIN cliente cl
            ON co.id_cliente = cl.id_cliente
        JOIN metodo_pago mp
            ON co.id_metodo_pago = mp.id_metodo_pago;
    """)

    with engine.connect() as conexion:
        df = pd.read_sql(query, conexion)

    tabla = pd.crosstab(
        df["genero"],
        df["metodo_pago"]
    )

    tabla_pct = pd.crosstab(
        df["genero"],
        df["metodo_pago"],
        normalize="index"
    ) * 100

    chi2, p_valor, grados_libertad, _ = (
        stats.chi2_contingency(tabla)
    )

    n = tabla.to_numpy().sum()
    k = min(tabla.shape)

    cramers_v = (
        chi2 / (n * (k - 1))
    ) ** 0.5

    # Cambiar 0/1 por nombres comprensibles
    tabla.index = [
        "Masculino" if genero == 0 else "Femenino"
        for genero in tabla.index
    ]

    tabla_pct.index = [
        "Masculino" if genero == 0 else "Femenino"
        for genero in tabla_pct.index
    ]

    return {
        "tabla_contingencia": tabla.to_dict(
            orient="index"
        ),

        "porcentajes_por_genero": (
            tabla_pct.round(2).to_dict(
                orient="index"
            )
        ),

        "chi_cuadrado": float(chi2),
        "p_valor": float(p_valor),
        "grados_libertad": int(grados_libertad),
        "cramers_v": float(cramers_v),
        "cantidad_registros": int(n)
    }


@mcp.tool()
def obtener_correlacion_boletin_vale() -> dict:
    """
    Analiza la relación estadística entre recibir boletín
    y utilizar vale mediante Chi-cuadrado y coeficiente Phi.
    """

    rutas = [
        "resultados/Venta_online_c.csv",
        "Venta_online_c.csv"
    ]

    df = None

    for ruta in rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=";")
            break

    if df is None:
        raise FileNotFoundError(
            "No se encontró Venta_online_c.csv"
        )

    tabla = pd.crosstab(
        df["Boletin"],
        df["Vale"]
    )

    porcentajes = pd.crosstab(
        df["Boletin"],
        df["Vale"],
        normalize="index"
    ) * 100

    chi2, p_valor, grados_libertad, _ = (
        stats.chi2_contingency(tabla)
    )

    n = tabla.to_numpy().sum()

    phi = (chi2 / n) ** 0.5

    return {
        "tabla_contingencia": {
            "sin_boletin": {
                "sin_vale": int(tabla.loc[0, 0]),
                "con_vale": int(tabla.loc[0, 1])
            },
            "con_boletin": {
                "sin_vale": int(tabla.loc[1, 0]),
                "con_vale": int(tabla.loc[1, 1])
            }
        },

        "porcentajes": {
            "sin_boletin": {
                "sin_vale": round(
                    float(porcentajes.loc[0, 0]), 2
                ),
                "con_vale": round(
                    float(porcentajes.loc[0, 1]), 2
                )
            },
            "con_boletin": {
                "sin_vale": round(
                    float(porcentajes.loc[1, 0]), 2
                ),
                "con_vale": round(
                    float(porcentajes.loc[1, 1]), 2
                )
            }
        },

        "chi_cuadrado": float(chi2),
        "p_valor": float(p_valor),
        "grados_libertad": int(grados_libertad),
        "phi": float(phi),
        "cantidad_clientes": int(n)
    }


@mcp.tool()
def analizar_boletin_vale() -> dict:
    """
    Analiza los patrones de compra y la relación estadística
    entre la recepción de boletines y el uso de vales.

    Incluye:
    - segmentación de clientes por boletín y vale
    - venta total promedio
    - número de compras promedio
    - monto de compra promedio
    - tabla de contingencia
    - porcentajes
    - prueba Chi-cuadrado
    - coeficiente Phi
    """

    rutas = [
        "resultados/Venta_online_c.csv",
        "Venta_online_c.csv"
    ]

    df = None

    for ruta in rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta, sep=";")
            break

    if df is None:
        raise FileNotFoundError(
            "No se encontró Venta_online_c.csv"
        )

    # --------------------------------------------------
    # SEGMENTACIÓN BOLETÍN / VALE
    # --------------------------------------------------

    segmento = (
        df.groupby(["Boletin", "Vale"])
        .agg(
            clientes=("Id_cliente", "count"),
            venta_promedio=("Venta_total", "mean"),
            compras_promedio=("N_Compras", "mean"),
            monto_promedio=("MontoCompra", "mean")
        )
        .round(2)
        .reset_index()
    )

    segmentacion = []

    for _, fila in segmento.iterrows():
        segmentacion.append({
            "boletin": (
                "Sí"
                if int(fila["Boletin"]) == 1
                else "No"
            ),
            "vale": (
                "Sí"
                if int(fila["Vale"]) == 1
                else "No"
            ),
            "clientes": int(fila["clientes"]),
            "venta_total_promedio": float(
                fila["venta_promedio"]
            ),
            "numero_compras_promedio": float(
                fila["compras_promedio"]
            ),
            "monto_compra_promedio": float(
                fila["monto_promedio"]
            )
        })

    # --------------------------------------------------
    # CORRELACIÓN BOLETÍN / VALE
    # --------------------------------------------------

    tabla = pd.crosstab(
        df["Boletin"],
        df["Vale"]
    )

    porcentajes = pd.crosstab(
        df["Boletin"],
        df["Vale"],
        normalize="index"
    ) * 100

    chi2, p_valor, grados_libertad, _ = (
        stats.chi2_contingency(tabla)
    )

    n = tabla.to_numpy().sum()

    phi = (chi2 / n) ** 0.5

    correlacion = {
        "tabla_contingencia": {
            "sin_boletin": {
                "sin_vale": int(tabla.loc[0, 0]),
                "con_vale": int(tabla.loc[0, 1])
            },
            "con_boletin": {
                "sin_vale": int(tabla.loc[1, 0]),
                "con_vale": int(tabla.loc[1, 1])
            }
        },

        "porcentajes": {
            "sin_boletin": {
                "sin_vale": round(
                    float(porcentajes.loc[0, 0]), 2
                ),
                "con_vale": round(
                    float(porcentajes.loc[0, 1]), 2
                )
            },
            "con_boletin": {
                "sin_vale": round(
                    float(porcentajes.loc[1, 0]), 2
                ),
                "con_vale": round(
                    float(porcentajes.loc[1, 1]), 2
                )
            }
        },

        "chi_cuadrado": float(chi2),
        "p_valor": float(p_valor),
        "grados_libertad": int(grados_libertad),
        "phi": float(phi),
        "cantidad_clientes": int(n)
    }

    return {
        "segmentacion": segmentacion,
        "relacion_estadistica": correlacion
    }


@mcp.tool()
def obtener_visualizaciones() -> dict:
    """
    Devuelve las visualizaciones realizadas por el equipo,
    indicando qué representa cada una.

    No genera nuevas imágenes. Informa sobre las gráficas
    existentes correspondientes a los análisis del proyecto.
    """

    graficos = {
        "3a_ranking_ventas_mes.png": {
            "punto": "3a",
            "titulo": "Ranking de facturación mensual",
            "descripcion": (
                "Compara el monto total facturado durante cada mes."
            ),
            "hallazgo_principal": (
                "Marzo presentó la mayor facturación con Q22,994.34 "
                "y noviembre la menor con Q19,779.24."
            )
        },

        "3b_preferencia_navegadores.png": {
            "punto": "3b",
            "titulo": "Preferencia de navegadores en compras en línea",
            "descripcion": (
                "Compara la cantidad de transacciones realizadas "
                "mediante los navegadores digitales."
            ),
            "hallazgo_principal": (
                "Navegador 1 fue el navegador web más utilizado "
                "con 1,273 transacciones."
            )
        },

        "3d_boletines_vales_mes.png": {
            "punto": "3d",
            "titulo": "Uso mensual de boletines y vales",
            "descripcion": (
                "Compara la utilización mensual de boletines y vales."
            ),
            "hallazgo_principal": (
                "Diciembre tuvo el mayor uso de boletines con 262 "
                "y marzo el mayor uso de vales con 133."
            )
        },

        "4a_edad_venta.png": {
            "punto": "4a",
            "titulo": "Comportamiento de compra por grupo de edad",
            "descripcion": (
                "Compara la venta total promedio entre diferentes "
                "rangos de edad."
            ),
            "hallazgo_principal": (
                "El grupo de 26 a 35 años tuvo la venta total "
                "promedio más alta, aproximadamente Q212.66."
            )
        },

        "4b_genero_compra.png": {
            "punto": "4b",
            "titulo": "Comportamiento de compra por género",
            "descripcion": (
                "Compara la distribución de Venta_total entre "
                "hombres y mujeres."
            ),
            "hallazgo_principal": (
                "El análisis no muestra diferencias importantes "
                "en el comportamiento de compra entre géneros."
            )
        },

        "4c_barras_boletin_vale.png": {
            "punto": "4c",
            "titulo": "Venta promedio por boletín y vale",
            "descripcion": (
                "Compara la venta total promedio según la recepción "
                "de boletín y utilización de vale."
            ),
            "hallazgo_principal": (
                "Los clientes que reciben boletín muestran una "
                "venta total promedio superior."
            )
        },

        "5c_boletin_vale.png": {
            "punto": "5c",
            "titulo": "Relación entre boletín y uso de vale",
            "descripcion": (
                "Representa los porcentajes de utilización de vales "
                "entre clientes con y sin boletín."
            ),
            "hallazgo_principal": (
                "Existe una asociación estadísticamente significativa "
                "entre recibir boletín y utilizar vale, aunque la "
                "intensidad de la asociación es débil."
            )
        }
    }

    carpeta = "graficos"

    for nombre, informacion in graficos.items():
        ruta = os.path.join(carpeta, nombre)

        informacion["archivo"] = ruta
        informacion["existe"] = os.path.exists(ruta)

    return {
        "cantidad_visualizaciones": len(graficos),
        "visualizaciones": graficos
    }


if __name__ == "__main__":
    mcp.run()