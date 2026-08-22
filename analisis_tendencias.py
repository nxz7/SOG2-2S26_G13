import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Verificar conexión
with engine.connect() as conexion:
    resultado = conexion.execute(text("SELECT 1"))
    print("Conexión a PostgreSQL correcta:", resultado.scalar())


# Meses con mayores y menores ventas

query_ventas_mes = """
SELECT
    EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes,
    SUM(monto_compra) AS monto_total,
    COUNT(*) AS cantidad_ventas
FROM compra
GROUP BY EXTRACT(MONTH FROM fecha_compra)
ORDER BY mes;
"""

ventas_mes = pd.read_sql_query(query_ventas_mes, engine)

ventas_mes["monto_total"] = ventas_mes["monto_total"].astype(float)

nombres_meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

ventas_mes["mes_nombre"] = ventas_mes["mes"].map(nombres_meses)

print("\nVENTAS POR MES")
print(ventas_mes)

mayor_venta = ventas_mes.loc[ventas_mes["monto_total"].idxmax()]
menor_venta = ventas_mes.loc[ventas_mes["monto_total"].idxmin()]

mayor_cantidad = ventas_mes.loc[ventas_mes["cantidad_ventas"].idxmax()]
menor_cantidad = ventas_mes.loc[ventas_mes["cantidad_ventas"].idxmin()]

print("\nMes con mayor facturación:")
print(
    mayor_venta["mes_nombre"],
    f'Q{mayor_venta["monto_total"]:,.2f}'
)

print("\nMes con menor facturación:")
print(
    menor_venta["mes_nombre"],
    f'Q{menor_venta["monto_total"]:,.2f}'
)

print("\nMes con mayor cantidad de transacciones:")
print(
    mayor_cantidad["mes_nombre"],
    mayor_cantidad["cantidad_ventas"]
)

print("\nMes con menor cantidad de transacciones:")
print(
    menor_cantidad["mes_nombre"],
    menor_cantidad["cantidad_ventas"]
)

# GRÁFICO 1
# Ranking de facturación mensual

ventas_ranking = ventas_mes.sort_values(
    by="monto_total",
    ascending=True
)

plt.figure(figsize=(10, 7))

barras = plt.barh(
    ventas_ranking["mes_nombre"],
    ventas_ranking["monto_total"]
)

plt.title("Ranking de facturación mensual")
plt.xlabel("Monto total de ventas (Q)")
plt.ylabel("Mes")

for barra, valor in zip(barras, ventas_ranking["monto_total"]):
    plt.text(
        barra.get_width() + 50,
        barra.get_y() + barra.get_height() / 2,
        f"Q{valor:,.2f}",
        va="center"
    )

plt.tight_layout()
plt.savefig("./graficos/3a_ranking_ventas_mes.png", dpi=300)
plt.show()


# Navegador más y menos utilizado

query_navegadores = """
SELECT
    n.id_navegador,
    n.nombre,
    COUNT(*) AS cantidad,
    SUM(c.monto_compra) AS monto_total
FROM compra c
INNER JOIN navegador n
    ON c.id_navegador = n.id_navegador
GROUP BY n.id_navegador, n.nombre
ORDER BY cantidad DESC;
"""

navegadores = pd.read_sql_query(query_navegadores, engine)

navegadores["monto_total"] = navegadores["monto_total"].astype(float)

total_compras = navegadores["cantidad"].sum()

navegadores["porcentaje"] = (
    navegadores["cantidad"] / total_compras * 100
)

print("\nUSO DE CANALES Y NAVEGADORES")
print(navegadores)

# GRÁFICO 2
# Uso de navegadores digitales

navegadores_web = navegadores[
    navegadores["id_navegador"] != 0
].copy()

navegadores_web = navegadores_web.sort_values(
    by="cantidad",
    ascending=True
)

plt.figure(figsize=(9, 5))

barras = plt.barh(
    navegadores_web["nombre"],
    navegadores_web["cantidad"]
)

plt.title("Preferencia de navegadores en compras en línea")
plt.xlabel("Cantidad de transacciones")
plt.ylabel("Navegador")

for barra, valor in zip(barras, navegadores_web["cantidad"]):
    plt.text(
        barra.get_width() + 10,
        barra.get_y() + barra.get_height() / 2,
        f"{valor:,}",
        va="center"
    )

plt.tight_layout()
plt.savefig("./graficos/3b_preferencia_navegadores.png", dpi=300)
plt.show()


# 3c. Ventas pagadas en efectivo

query_efectivo = """
SELECT
    COUNT(*) AS cantidad_ventas,
    SUM(monto_compra) AS monto_total
FROM compra
WHERE id_metodo_pago = 0;
"""

efectivo = pd.read_sql_query(query_efectivo, engine)

cantidad_efectivo = int(efectivo.loc[0, "cantidad_ventas"])
monto_efectivo = float(efectivo.loc[0, "monto_total"])

query_total = """
SELECT COUNT(*) AS total
FROM compra;
"""

total = int(
    pd.read_sql_query(query_total, engine).loc[0, "total"]
)

porcentaje_efectivo = cantidad_efectivo / total * 100

print("\nVENTAS EN EFECTIVO")
print(f"Cantidad: {cantidad_efectivo:,}")
print(f"Monto: Q{monto_efectivo:,.2f}")
print(f"Porcentaje: {porcentaje_efectivo:.2f}%")


# 3d. Uso mensual de boletines y vales

query_promociones = """
SELECT
    EXTRACT(MONTH FROM fecha_compra)::INTEGER AS mes,

    SUM(
        CASE
            WHEN boletin = 1 THEN 1
            ELSE 0
        END
    )::INTEGER AS boletines,

    SUM(
        CASE
            WHEN vale = 1 THEN 1
            ELSE 0
        END
    )::INTEGER AS vales

FROM compra
GROUP BY EXTRACT(MONTH FROM fecha_compra)
ORDER BY mes;
"""

promociones = pd.read_sql_query(query_promociones, engine)

promociones["mes_nombre"] = promociones["mes"].map(nombres_meses)

print("\nBOLETINES Y VALES POR MES")
print(promociones)

mayor_boletin = promociones.loc[
    promociones["boletines"].idxmax()
]

menor_boletin = promociones.loc[
    promociones["boletines"].idxmin()
]

mayor_vale = promociones.loc[
    promociones["vales"].idxmax()
]

menor_vale = promociones.loc[
    promociones["vales"].idxmin()
]

print(
    "\nMayor uso de boletines:",
    mayor_boletin["mes_nombre"],
    mayor_boletin["boletines"]
)

print(
    "Menor uso de boletines:",
    menor_boletin["mes_nombre"],
    menor_boletin["boletines"]
)

print(
    "Mayor uso de vales:",
    mayor_vale["mes_nombre"],
    mayor_vale["vales"]
)

print(
    "Menor uso de vales:",
    menor_vale["mes_nombre"],
    menor_vale["vales"]
)

# GRÁFICO 3
# Uso mensual de boletines y vales

x = np.arange(len(promociones))
ancho = 0.38

plt.figure(figsize=(12, 6))

plt.bar(
    x - ancho / 2,
    promociones["boletines"],
    ancho,
    label="Boletín"
)

plt.bar(
    x + ancho / 2,
    promociones["vales"],
    ancho,
    label="Vale"
)

plt.xticks(
    x,
    promociones["mes_nombre"],
    rotation=45
)

plt.title("Uso mensual de boletines y vales")
plt.xlabel("Mes")
plt.ylabel("Cantidad de transacciones")
plt.legend()

plt.tight_layout()
plt.savefig("./graficos/3d_boletines_vales_mes.png", dpi=300)
plt.show()