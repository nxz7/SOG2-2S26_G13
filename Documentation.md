# Diagrama Entidad Relación
![image](https://hackmd.io/_uploads/B1POHiGDMl.png)

## 1. Preparación de datos

**Tipos de datos:**

- Enteros: `Edad`, `Genero`, `N_Compras`, `MetodoPago`, `Tiempo`, `Navegador`, `Boletin`, `Vale`
- Decimales: `Venta_total`, `MontoCompra`
- `FechaCompra` viene como texto en formato `dd.mm.yy` (ej. `02.02.21`), se convirtió a tipo fecha real para poder agrupar por mes/trimestre.

**Validación de dominios:** Se confirmó que las variables categóricas están dentro de los rangos que define el enunciado, sin valores fuera de catálogo:

- `Genero`: 0/1 (3,372 masculino, 3,128 femenino)
- `MetodoPago`: 0/1/2 (efectivo 1,207; tarjeta de crédito 3,827; tarjeta de débito 1,466)
- `Navegador`: 0–4 (0 = tienda física, con 3,523 registros; el resto repartido entre los 4 navegadores)
- `Boletin` y `Vale`: 0/1

**Diseño relacional:** Para cargarlo a la base de datos SQL en la nube no se dejará como una sola tabla plana, se normalizó en 4 tablas (como en la imagen inicial): `CLIENTE`, `COMPRA`, `METODO_PAGO` y `NAVEGADOR`, usando `MetodoPago` y `Navegador` como catálogos con clave foránea en vez de repetir el código numérico directamente en cada registro. `Venta_total` y `N_Compras` no se guardan como columnas fijas del cliente, sino que se calculan con una vista/consulta agregada sobre `COMPRA`, así se evita que esos totales queden desactualizados si se insertan nuevas compras.

Ejemplo:
``` mermaid
flowchart LR
    A[CSV original] --> B[CLIENTE]
    A --> C[COMPRA]

    B -->|1:N| C

    C --> D["COUNT(*)<br/>N_Compras"]
    C --> E["SUM(monto_compra)<br/>Venta_total"]

    D --> F["Datos calculados"]
    E --> F
```

Se hizo una verificación adicional, el dataset no tiene valores nulos, y tampoco hay filas duplicadas ni Id_cliente repetidos (cada cliente aparece una sola vez). No fue necesario imputar ni eliminar registros.

### Diagrama ER

- **CLIENTE** (`id_cliente` PK, `edad`, `genero`): 1 cliente puede tener muchas compras.
- **COMPRA** (`id_compra` PK, `id_cliente` FK, `fecha_compra`, `monto_compra`, `tiempo_seg`, `boletin`, `vale`, `id_metodo_pago` FK, `id_navegador` FK): tabla de hechos, una fila por transacción.
- **METODO_PAGO** (`id_metodo_pago` PK, `nombre`): catálogo: Efectivo / Tarjeta de crédito / Tarjeta de débito.
- **NAVEGADOR** (`id_navegador` PK, `nombre`): catálogo: Tienda física / Navegador 1–4.

### Planificación del proyecto

**División de tareas:** Se dividió el trabajo siguiendo las fases del alcance de la práctica:

1. Preparación de datos y modelado de base de datos.
2. Análisis exploratorio y visualizaciones.
3. Análisis de tendencias, segmentación y correlaciones.
4. Construcción del agente conversacional con Google ADK + MCP Server.
5. Redacción del informe final y respuestas a las preguntas de discusión.


**Herramientas y tecnologías:** Se usó Python (pandas para limpieza y análisis, matplotlib/seaborn o Power BI para visualizaciones) por su rapidez para manipular datos tabulares; una base de datos relacional en la nube (ej. Supabase/PostgreSQL o Azure SQL) para cumplir el requisito de "base de datos en la nube"; Google ADK para el agente conversacional, con un MCP Server propio que expone los resultados del análisis como herramientas consultables por el agente; y GitHub como repositorio para versionar el código.


### Proceso de análisis

Para preparar los datos se siguió un enfoque secuencial: primero se hizo una inspección inicial (`shape`, tipos de dato, `describe()`) para entender la estructura del CSV; luego se verificaron nulos y duplicados de forma explícita en vez de asumir que el archivo venía limpio; después se validó que cada variable categórica cayera dentro del dominio esperado (por ejemplo, que `Navegador` solo tuviera valores 0–4), y finalmente se convirtió `FechaCompra` a un tipo de dato fecha real, ya que venía como texto con formato `dd.mm.yy`, lo cual habría impedido agrupar u ordenar correctamente por mes.

Durante el análisis exploratorio, una de las decisiones importantes fue normalizar el CSV plano en varias tablas relacionadas en lugar de cargarlo tal cual a la base de datos. Aunque cargar el archivo "tal cual" hubiera sido más rápido, se prefirió separar los catálogos (`MetodoPago`, `Navegador`) de la tabla de compras para evitar redundancia y facilitar consultas SQL más limpias (por ejemplo, `JOIN` en vez de comparar números mágicos).

Un desafío durante el análisis fue interpretar correctamente la columna `Navegador`, ya que el valor 0 no representa "sin navegador" sino "tienda física", es decir, el dataset descrito como "ventas online del año 2021" en realidad ya mezcla ambos canales (54% tienda física, 46% en línea repartido entre 4 navegadores). Esto se documentó explícitamente para que el análisis de canales no se interpretara como si todo el dataset fuera puramente digital, lo cual es justamente relevante para la empresa que quiere expandirse a una sucursal física.

``` python
import pandas as pd
from sqlalchemy import create_engine

# 1. Lectura
df = pd.read_csv('Venta_online_c.csv', sep=';')

print(f"Registros: {df.shape[0]} | Columnas: {df.shape[1]}")
print(df.dtypes)
print(df.describe())

# 2. Nulos y duplicados
print("\nNulos:\n", df.isnull().sum())
print(f"\nFilas duplicadas: {df.duplicated().sum()}")

# 3. Validación de dominios
dominios = {
    'Genero': {0, 1},
    'MetodoPago': {0, 1, 2},
    'Navegador': {0, 1, 2, 3, 4},
    'Boletin': {0, 1},
    'Vale': {0, 1}
}

for columna, validos in dominios.items():
    fuera = set(df[columna].unique()) - validos
    print(f"{columna}: {'OK' if not fuera else fuera}")

# 4. Conversión de fecha
df['FechaCompra'] = pd.to_datetime(
    df['FechaCompra'],
    format='%d.%m.%y'
)
df['Mes'] = df['FechaCompra'].dt.month

# 5. Catálogos
metodo_pago = pd.DataFrame({
    'id_metodo_pago': [0, 1, 2],
    'nombre': [
        'Efectivo',
        'Tarjeta de crédito',
        'Tarjeta de débito'
    ]
})

navegador = pd.DataFrame({
    'id_navegador': [0, 1, 2, 3, 4],
    'nombre': [
        'Tienda física',
        'Navegador 1',
        'Navegador 2',
        'Navegador 3',
        'Navegador 4'
    ]
})

# 6. Tabla cliente
cliente = df[
    ['Id_cliente', 'Edad', 'Genero']
].rename(columns={
    'Id_cliente': 'id_cliente',
    'Edad': 'edad',
    'Genero': 'genero'
})

# 7. Tabla compra
compra = df[
    [
        'Id_cliente',
        'FechaCompra',
        'MontoCompra',
        'Tiempo',
        'MetodoPago',
        'Navegador',
        'Boletin',
        'Vale'
    ]
].rename(columns={
    'Id_cliente': 'id_cliente',
    'FechaCompra': 'fecha_compra',
    'MontoCompra': 'monto_compra',
    'Tiempo': 'tiempo_seg',
    'MetodoPago': 'id_metodo_pago',
    'Navegador': 'id_navegador',
    'Boletin': 'boletin',
    'Vale': 'vale'
})

compra.insert(0, 'id_compra', range(1, len(compra) + 1))

```

### Conclusión

Uno de los hallazgos más relevantes del análisis es que la edad del cliente no presenta una relación lineal significativa con el comportamiento de compra dentro de este dataset. Al calcular la correlación entre `Edad` y `Venta_total` se obtiene un valor de -0.025, y entre `Edad` y `N_Compras` de -0.05, ambos prácticamente nulos.

![image](https://hackmd.io/_uploads/Hk7LS3GPGe.png)


Esto se confirma al segmentar a los clientes en grupos etarios: el grupo de 18-25 años gasta en promedio Q207.8 con 5.27 compras, el de 26-35 años gasta Q212.7 con 5.25 compras, el de 36-45 años gasta Q204.7 con 5.04 compras, y así sucesivamente hasta el grupo de 56-79 años con Q192.5 y 4.73 compras.

![image](https://hackmd.io/_uploads/HJsKS3GvMl.png)


Las diferencias entre grupos son mínimas, lo que indica que el gasto promedio y la frecuencia de compra se mantienen relativamente estables a lo largo de todo el rango de edades (18 a 79 años) representado en la base de datos.

Esto contrasta con la intuición inicial de que los clientes más jóvenes, por estar más habituados a comprar en línea, tenderían a gastar más o comprar con mayor frecuencia que los clientes de mayor edad, o viceversa. En la práctica, ninguno de los dos extremos se cumple de forma marcada.

Este hallazgo tiene una implicación directa para el negocio: no conviene diseñar estrategias de marketing, promociones o segmentación basadas principalmente en la edad del cliente, ya que esta variable no está explicando de forma significativa las diferencias en el valor de compra.

En su lugar, otras variables del dataset sí muestran relaciones más claras y accionables, como el canal de compra (tienda física representa el 54% de los registros frente a 46% en línea) o el uso combinado de boletines y vales, donde los clientes que reciben boletín tienen una probabilidad notablemente mayor de usar vale (811 de 2,921, contra 443 de 3,579 sin boletín).

![image](https://hackmd.io/_uploads/Hk-NLhMPGg.png)
![image](https://hackmd.io/_uploads/rkNLI3GDMx.png)


Esto sugiere que la empresa debería reorientar sus esfuerzos de segmentación hacia el comportamiento transaccional y el canal de interacción del cliente, en lugar de asumir que la demografía por edad es un buen predictor de valor o lealtad.

Para una empresa que está a punto de abrir una sucursal física y ya reporta un porcentaje mayoritario de ventas por ese canal, esta conclusión también refuerza que la inversión en experiencia física y digital se debe pensar de forma transversal a todas las edades, y no como una estrategia dirigida solo a un segmento etario específico.

### Acciones concretas

1. **Rediseñar las campañas de marketing y fidelización basándolas en comportamiento transaccional (canal, uso de boletín/vale) en vez de en la edad del cliente**, ya que los datos muestran que la edad no diferencia el gasto ni la frecuencia de compra, mientras que sí existe una relación clara entre recibir boletín y usar vale. La empresa puede usar el boletín como palanca activa para incrementar el uso de vales y, con ello, la recurrencia de compra.

2. **Diseñar la sucursal física y el catálogo digital como canales complementarios y no como audiencias separadas**, dado que el 54% de las transacciones ya ocurren en tienda física frente a un 46% distribuido entre los 4 navegadores. Esto implica invertir en integrar inventario y promociones entre ambos canales (ej. vales/boletines válidos en cualquiera de los dos) en lugar de tratar la apertura de la sucursal como un canal nuevo e independiente del negocio online ya existente.

## Análisis de tendencias

**Ventas por mes:**

Para identificar los meses con mayor y menor nivel de ventas se agruparon las compras según el mes de `fecha_compra` y se calculó tanto el monto total vendido como la cantidad de transacciones realizadas durante cada período.

El mes con mayor facturación fue **marzo**, con un total de **Q22,994.34**, mientras que **noviembre** presentó la menor facturación del año con **Q19,779.24**.

Al analizar la cantidad de transacciones se identificó que **diciembre** fue el mes con mayor número de compras, con **577 transacciones**, mientras que **noviembre** registró la menor cantidad con **493 transacciones**.

Un aspecto relevante es que el mes con mayor cantidad de compras no coincide con el mes de mayor facturación. Aunque diciembre registró más transacciones, marzo obtuvo un monto total de ventas superior. Esto indica que la cantidad de compras por sí sola no determina los ingresos generados, ya que también interviene el monto de cada transacción.

![image](./graficos/3a_ranking_ventas_mes.png)

**Preferencia de navegadores:**

Para determinar el navegador más y menos utilizado se contabilizaron las transacciones asociadas con cada uno de los valores registrados en el catálogo `NAVEGADOR`.

La **tienda física** representa el principal canal de compra dentro del conjunto de datos, con **3,523 transacciones**, equivalentes aproximadamente al **54.20%** de las 6,500 compras registradas.

Debido a que el valor `0` corresponde a tienda física y no a un navegador web, para responder específicamente cuál es el navegador más y menos utilizado se analizaron únicamente los canales digitales.

Entre estos, el **Navegador 1** fue el más utilizado con **1,273 transacciones**, seguido del Navegador 2 con 847 y del Navegador 3 con 660. El **Navegador 4** fue el menos utilizado con únicamente **197 transacciones**.

La diferencia entre el Navegador 1 y el Navegador 4 muestra que los clientes presentan una preferencia considerable por determinados entornos de navegación al momento de realizar sus compras en línea.

![image](./graficos/3b_preferencia_navegadores.png)

**Ventas realizadas mediante efectivo:**

Para identificar las ventas pagadas en efectivo se filtraron las compras cuyo `id_metodo_pago` corresponde al valor `0`, definido dentro del catálogo como **Efectivo**.

Se identificaron **1,207 transacciones** realizadas mediante esta modalidad de pago, equivalentes aproximadamente al **18.57%** del total de compras registradas. Estas operaciones representan un monto acumulado de **Q47,465.64**.

El enunciado de la práctica también hace referencia a ventas realizadas contra entrega. Sin embargo, el conjunto de datos proporcionado no contiene una categoría independiente que permita identificar específicamente este tipo de operación. Los métodos disponibles únicamente corresponden a efectivo, tarjeta de crédito y tarjeta de débito.

Por esta razón, el análisis se realizó utilizando exclusivamente la categoría de **pago en efectivo**, evitando asumir o generar información que no se encuentra representada directamente en los datos.

**Uso de boletines y vales por mes:**

Para analizar el comportamiento mensual de los boletines y vales se agruparon las transacciones según el mes de compra y se contabilizaron aquellos registros cuyo valor de `boletin` o `vale` corresponde a `1`.

En el caso de los boletines, **diciembre** presentó la mayor cantidad de registros con **262**, seguido de marzo con 261 y octubre con 260. El menor uso de boletines se registró durante **septiembre**, con **200**.

En cuanto a los vales, **marzo** fue el mes con mayor utilización, alcanzando **133 registros**, seguido de diciembre con 128 y septiembre con 120. El menor uso se produjo durante **octubre**, con únicamente **85 registros**.

Los resultados permiten observar que los boletines y los vales no presentan exactamente el mismo comportamiento durante el año. Mientras que el mayor uso de boletines ocurre en diciembre, los vales alcanzan su valor máximo durante marzo. Esto indica que ambas herramientas pueden estar siendo utilizadas de manera diferente por los clientes.

![image](./graficos/3d_boletines_vales_mes.png)

### Metodología de visualizaciones

Para representar los resultados obtenidos durante el análisis de tendencias se seleccionaron tres visualizaciones diferentes, considerando el tipo de información analizada y evitando repetir gráficas que ya habían sido utilizadas durante el análisis exploratorio.

Para las ventas mensuales se utilizó un **gráfico de barras horizontales ordenado según el monto total de facturación**. Este tipo de representación permite comparar directamente los doce meses e identificar de forma sencilla aquellos que presentan los valores más altos y más bajos. Al ordenar los períodos según su facturación se facilita particularmente la identificación de marzo como el mes con mayor monto vendido y noviembre como el de menor facturación.

Para la preferencia de navegadores se utilizó un **gráfico de barras horizontales** tomando únicamente los navegadores asociados con las compras en línea. Este tipo de visualización es apropiado para comparar variables categóricas, debido a que permite observar claramente las diferencias en la cantidad de transacciones registradas por cada navegador. Se decidió separar la tienda física de esta gráfica debido a que representa un canal de compra diferente y no un navegador web.

Finalmente, para analizar la utilización de boletines y vales se seleccionó un **gráfico de barras agrupadas por mes**. Esta representación permite visualizar ambas variables dentro de un mismo período y realizar una comparación directa de su comportamiento durante los doce meses del año. De esta manera se pueden reconocer fácilmente los meses con mayor y menor utilización de cada herramienta y comprobar que ambas presentan tendencias diferentes.

### Conclusión

El análisis de tendencias permitió identificar que las ventas presentan variaciones durante el año, aunque sin una concentración excesiva en un único período. Marzo registró la mayor facturación con Q22,994.34, mientras que noviembre presentó el menor monto vendido con Q19,779.24. Sin embargo, diciembre fue el mes con mayor cantidad de transacciones, demostrando que un mayor número de compras no necesariamente representa una mayor facturación.

También se identificó una participación importante de la tienda física, que concentra el 54.20% de las transacciones. Dentro de los canales digitales, el Navegador 1 fue el más utilizado, mientras que el Navegador 4 presentó una utilización considerablemente menor. Esta diferencia evidencia la necesidad de analizar las causas que influyen en la preferencia de los clientes por determinados canales de compra.

Por otra parte, las compras realizadas en efectivo representan el 18.57% de las transacciones, mientras que el comportamiento mensual de boletines y vales mostró tendencias diferentes. Diciembre presentó el mayor uso de boletines y marzo el mayor uso de vales, indicando que ambas herramientas promocionales no necesariamente son utilizadas de la misma manera durante el año.

En conjunto, los resultados muestran que el desempeño comercial debe evaluarse considerando no solamente el monto vendido, sino también la cantidad de transacciones, el canal utilizado y el comportamiento de las herramientas promocionales. Estos hallazgos pueden servir como base para orientar campañas en meses de menor desempeño, fortalecer los canales digitales y utilizar de forma más estratégica los boletines y vales.

### Acciones concretas

1. **Implementar campañas promocionales durante los meses con menor desempeño comercial**, principalmente en noviembre, utilizando boletines y vales como mecanismos de incentivo para aumentar la cantidad de compras. Posteriormente se puede comparar el comportamiento de las ventas antes y después de las campañas para determinar cuál de estas herramientas genera mejores resultados.

2. **Investigar las causas de la baja utilización del Navegador 4 y mejorar la experiencia de compra en los canales digitales menos utilizados**, evaluando factores como compatibilidad, tiempos de carga, facilidad de navegación y funcionamiento del proceso de compra. Esta información puede utilizarse para reducir las diferencias existentes entre los diferentes navegadores y fortalecer el canal de ventas en línea.

