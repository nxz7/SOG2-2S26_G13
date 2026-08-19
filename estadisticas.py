#!/usr/bin/env python3
import pandas as pd

# data a analizar
VARIABLES = ["Edad", "Venta_total", "MontoCompra", "Tiempo"]
# cargalos
dataFull = pd.read_csv("Venta_online_c.csv", sep=";")

resultados = []

for variable in VARIABLES:
    # quitaVacios y nulos
    serie = dataFull[variable].dropna()  
    # calcular en general
    conteo = serie.value_counts()
    moda = conteo.index[0]
    frecuencia_moda = conteo.iloc[0]

    # las stats que va a mostrar
    resultados.append({
        "variable": variable,
        "media": serie.mean(),
        "mediana": serie.median(),
        "moda": moda,
        "frecuencia_moda": frecuencia_moda,
        "desviacion_estandar": serie.std(),
        "minimo": serie.min(),
        "maximo": serie.max(),
        "n": serie.count(),
    })


# giardar la data
tabla = pd.DataFrame(resultados)
print(tabla.to_string(index=False))
tabla.to_csv("estadisticas_inciso2.csv", index=False, float_format="%.6f")