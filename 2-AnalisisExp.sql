-- ====================2 - exploratorio==========================0
-- EDAD
SELECT AVG(edad)::numeric(14,3) AS media_edad, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY edad)::numeric(14,3) AS mediana_edad,
    MODE() WITHIN GROUP (ORDER BY edad) AS moda_edad
FROM cliente;

-- Venta total por cliente
WITH venta_por_cliente AS ( SELECT   c.id_cliente,   COALESCE(SUM(co.monto_compra), 0) AS venta_total
    FROM cliente c
    LEFT JOIN compra co ON co.id_cliente = c.id_cliente GROUP BY c.id_cliente)
SELECT AVG(venta_total)::numeric(14,3) AS media_ventatotal,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total)::numeric(14,3)  AS mediana_ventatotal,
    MODE() WITHIN GROUP (ORDER BY venta_total)  AS moda_ventatotal
FROM venta_por_cliente;


-- MONTO POR COMPRA
SELECT
    AVG(monto_compra)::numeric(14,3) AS media_TOTALcompra,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monto_compra)::numeric(14,3)  AS mediana_TOTALcompra,
    MODE() WITHIN GROUP (ORDER BY monto_compra) AS moda_TOTALcompra
FROM compra;

-- tiempo por compra
SELECT
    AVG(tiempo_seg)::numeric(14,3) AS media_segCompra,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tiempo_seg)::numeric(14,3) AS mediana_segCompra,
    MODE() WITHIN GROUP (ORDER BY tiempo_seg) AS moda_segCompra
FROM compra;