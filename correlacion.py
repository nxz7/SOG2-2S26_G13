

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


df = pd.read_csv("Venta_online_c.csv", sep=";")


# ==================================================================

#  CON SKNEWNESS SE MIRA QUE TAN SIMETRICA ES LA VARIABLE, PARA EVITAR PERSON ENGAÑOSO
skew_venta = df['Venta_total'].skew()
skew_edad = df['Edad'].skew()
print(f">>SIMETRIA Venta_total: {skew_venta:.2f}")   # 3.13 -> muy sesgada a la derecha
print(f">>SIMETRIA Edad: {skew_edad:.2f}")            # 0.31 -> casi simétrica

# SE CALCULA PERSON
pear_r, pear_p = stats.pearsonr(df['Edad'], df['Venta_total'])
print(f"\n>>Pearson r = {pear_r:.4f}")
print(f" pvalor = {pear_p:.4g}")


# SPEARMAN TRABAJA CON RANGOS, ES MEJOR YA QUE VENTAS ESTA MUY SESAGADA
spear_r, spear_p = stats.spearmanr(df['Edad'], df['Venta_total'])
print(f">>Spearman rho = {spear_r:.4f} ")
print(f"pValor = {spear_p:.4g}")



# r2 indica que tan bien se ajusta
slope, intercept, r_value, p_value, std_err = stats.linregress(  df['Edad'], df['Venta_total'])
print("------------REGRESION LINEAL SIMPLE------------")
print(f"\n FROMULA > Venta_total = {intercept:.2f} + ({slope:.3f} * Edad)")
print(f"R2 = {r_value**2:.5f}  ")


fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(df['Edad'], df['Venta_total'], alpha=0.25, s=14, color="#788ce7")
x_line = np.array([df['Edad'].min(), df['Edad'].max()])
y_line = intercept + slope * x_line
ax.plot(x_line, y_line, color="#db90e2", linewidth=2.5,
        label=f'y = {intercept:.1f} + ({slope:.2f})x | R²={r_value**2:.4f}')
ax.set_title('RelaciOn Edad - Venta Total', fontsize=15, fontweight='bold')
ax.set_xlabel('Edad del cliente')
ax.set_ylabel('Venta total (Q)')
ax.legend()
plt.tight_layout()
plt.savefig('RELACION_edad_venta.png', dpi=150)
plt.close()



# ----------------------------------------

# GENERO Y PAGO
# se hace la tabla porqiue los numeros solo son valores que representan catgeorias tipo 0/1/2 no son valores
# contingencia, mira la relacion entre dos categorias cruzando frecuencias
tabla = pd.crosstab(df['Genero'], df['MetodoPago'])
print("\n--------------------------------------")
print("\n----------------GENERO-PAGO--------")
print("\nTABLA:")
print(tabla)

tabla_pct = pd.crosstab(df['Genero'], df['MetodoPago'], normalize='index') * 100
print("\nTabla % por fila / género):")
print(tabla_pct.round(2))

# CHI CUADRADO COMPARA las frecuencias que estan contra las que se esperarias si no hay relacion
# es la que se usa para este tipo la H0 es que son independientes
print(f"\n-------------- CHI CUADRADO: si hay o no hay relacion")
chi2, p_chi2, dof, expected = stats.chi2_contingency(tabla)
print(f"\n>>chiCUAD = {chi2:.4f}, p-valor = {p_chi2:.4g}, gl = {dof}")

#print("Frecuencias esperadas bajo independencia:")
#print(pd.DataFrame(expected, index=tabla.index, columns=tabla.columns).round(1))

# ------------------------------------------------------------------

print(f"\nCramers mide que tan fuerte")
n = tabla.sum().sum()
k = min(tabla.shape)
cramers_v = (chi2 / (n * (k - 1))) ** 0.5
print(f"\nCramerss V = {cramers_v:.4f}")

# ------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5.5))
colores_metodo = ["#d39ce9", "#abf1af", "#fddf7a"]
bottom = np.zeros(2)
etiquetas_genero = ['Género 0', 'Género 1']
for i, col in enumerate(tabla_pct.columns):
    vals = tabla_pct[col].values
    ax.bar(etiquetas_genero, vals, bottom=bottom,
           label=f'Método {col}', color=colores_metodo[i], edgecolor='white')
    for j, v in enumerate(vals):
        ax.text(j, bottom[j] + v / 2, f'{v:.1f}%', ha='center', va='center',
                fontsize=9, color='white', fontweight='bold')
    bottom += vals
ax.set_title('Distribucion del metodo de pago segun  género', fontsize=14, fontweight='bold')
ax.set_ylabel('Porcentaje de clientes ')
ax.set_xlabel('Genero')
ax.legend(title='Metodo pago', bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.savefig('RELACION_GENERO_PAGOO.png', dpi=150)
plt.close()

print("\n\n!!!!!!!!!!!!!!! FIN")