import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
df = pd.read_csv(
    "resultados/Venta_online_c.csv",
    sep=";"
)

# 4a. SEGMENTACIÓN POR EDAD
rangos_edad = [17, 25, 35, 45, 55, 79]
nombres_rangos = ["18-25", "26-35", "36-45", "46-55", "56-79"]

df["GrupoEdad"] = pd.cut(
    df["Edad"],
    bins=rangos_edad,
    labels=nombres_rangos,
    include_lowest=True
)

segmento_edad = df.groupby(
    "GrupoEdad",
    observed=True
).agg(
    clientes=("Id_cliente", "count"),
    venta_promedio=("Venta_total", "mean"),
    compras_promedio=("N_Compras", "mean"),
    monto_promedio=("MontoCompra", "mean")
).round(2)

print("\nSEGMENTACIÓN POR EDAD")
print(segmento_edad)

fig, eje = plt.subplots(figsize=(12, 8))
posiciones = range(len(nombres_rangos))
promedios_edad = segmento_edad["venta_promedio"].to_numpy()

eje.fill_between(
    list(posiciones),
    promedios_edad,
    color="#8DB62E",
    alpha=0.15
)
eje.plot(
    list(posiciones),
    promedios_edad,
    color="#000345",
    marker="o",
    markersize=8,
    linewidth=2.5
)

eje.set_xticks(list(posiciones), nombres_rangos)
eje.set_title("Comportamiento de compra por grupo de edad")
eje.set_xlabel("Grupo de edad (ordinal)")
eje.set_ylabel("Venta total promedio (Q)")
eje.grid(axis="y", alpha=0.25)

for posicion, valor in zip(posiciones, promedios_edad):
    eje.annotate(
        f"Q{valor:.2f}",
        (posicion, valor),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center"
    )

fig.tight_layout()
fig.savefig("graficos/4a_edad_venta.png", dpi=300)
plt.close(fig)



# 4b. COMPARACIÓN POR GENERO
segmento_genero = df.groupby("Genero").agg(
    clientes=("Id_cliente", "count"),
    venta_promedio=("Venta_total", "mean"),
    compras_promedio=("N_Compras", "mean"),
    monto_promedio=("MontoCompra", "mean")
).round(2)

print("\nSEGMENTACIÓN POR GÉNERO")
print(segmento_genero)

generos = ["Masculino", "Femenino"]
ventas_por_genero = [
    df.loc[df["Genero"] == genero, "Venta_total"]
    for genero in [0, 1]
]

plt.figure(figsize=(8, 5))
boxplot = plt.boxplot(
    ventas_por_genero,
    tick_labels=generos,
    patch_artist=True,
    showmeans=True,
    meanprops={"marker": "D", "markerfacecolor": "black", "markeredgecolor": "black"}
)

for caja, color in zip(boxplot["boxes"], ["#6A9FB5", "#D98B8B"]):
    caja.set_facecolor(color)
    caja.set_alpha(0.75)

plt.title("Comportamiento de compra por género")
plt.xlabel("Género")
plt.ylabel("Venta total del cliente (Q)")
plt.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig("graficos/4b_genero_compra.png", dpi=300)
plt.close()


# 4c. SEGMENTACIÓN POR BOLETÍN Y VALE
segmento_promociones = df.groupby(
    ["Boletin", "Vale"]
).agg(
    clientes=("Id_cliente", "count"),
    venta_promedio=("Venta_total", "mean"),
    compras_promedio=("N_Compras", "mean"),
    monto_promedio=("MontoCompra", "mean")
).round(2)

print("\nSEGMENTACIÓN POR BOLETÍN Y VALE")
print(segmento_promociones)

segmento_promociones.to_csv(
    "resultados/segmentacion_boletin_vale.csv"
)

etiquetas_boletin = ["Sin boletín", "Con boletín"]
sin_vale = [
    segmento_promociones.loc[(0, 0), "venta_promedio"],
    segmento_promociones.loc[(1, 0), "venta_promedio"]
]
con_vale = [
    segmento_promociones.loc[(0, 1), "venta_promedio"],
    segmento_promociones.loc[(1, 1), "venta_promedio"]
]

posiciones_boletin = range(len(etiquetas_boletin))
ancho_barra = 0.35

fig, eje = plt.subplots(figsize=(8, 6))
barras_sin = eje.bar(
    [p - ancho_barra / 2 for p in posiciones_boletin],
    sin_vale,
    width=ancho_barra,
    label="Sin vale",
    color="#934C63"
)
barras_con = eje.bar(
    [p + ancho_barra / 2 for p in posiciones_boletin],
    con_vale,
    width=ancho_barra,
    label="Con vale",
    color="#02582D"
)

eje.set_xticks(list(posiciones_boletin), etiquetas_boletin)
eje.set_title("Venta promedio por boletín y vale (patrones de compra)")
eje.set_xlabel("Recepción de boletín")
eje.set_ylabel("Venta total promedio (Q)")
eje.legend(title="Uso de vale")
eje.grid(axis="y", alpha=0.25)
eje.bar_label(barras_sin, padding=3, fmt="Q%.2f")
eje.bar_label(barras_con, padding=3, fmt="Q%.2f")

fig.tight_layout()
fig.savefig("graficos/4c_barras_boletin_vale.png", dpi=300)
plt.close(fig)


# --------------------------------------------------------------------

# 5c. RELACIÓN ENTRE BOLETÍN Y VALE

tabla_boletin_vale = pd.crosstab(
    df["Boletin"],
    df["Vale"]
)

print("\n----------- BOLETÍN Y VALE -----------")
print(tabla_boletin_vale)

porcentajes_boletin_vale = pd.crosstab(
    df["Boletin"],
    df["Vale"],
    normalize="index"
) * 100

print("\nPorcentajes por grupo de boletín:")
print(porcentajes_boletin_vale.round(2))

chi2, p_valor, grados_libertad, esperados = stats.chi2_contingency(
    tabla_boletin_vale
)

n = tabla_boletin_vale.to_numpy().sum()
phi = (chi2 / n) ** 0.5

print(f"\nChi-cuadrado: {chi2:.4f}")
print(f"Valor p: {p_valor:.6f}")
print(f"Grados de libertad: {grados_libertad}")
print(f"Coeficiente Phi: {phi:.4f}")

ax = porcentajes_boletin_vale.plot(
    kind="bar",
    stacked=True,
    color=["#D8B7E2", "#F4D961"],
    figsize=(8, 5)
)

ax.set_title("Relación entre boletín y uso de vale")
ax.set_xlabel("Recepción de boletín")
ax.set_ylabel("Porcentaje (%)")
ax.set_xticklabels(["Sin boletín", "Con boletín"], rotation=0)
ax.legend(["Sin vale", "Con vale"], title="Uso de vale")

for fila in range(len(porcentajes_boletin_vale)):
    acumulado = 0
    for columna in porcentajes_boletin_vale.columns:
        valor = porcentajes_boletin_vale.iloc[fila][columna]
        ax.text(
            fila,
            acumulado + valor / 2,
            f"{valor:.2f}%",
            ha="center",
            va="center",
            fontsize=9
        )
        acumulado += valor

plt.tight_layout()
plt.savefig(
    "graficos/5c_boletin_vale.png",
    dpi=300
)
plt.close()