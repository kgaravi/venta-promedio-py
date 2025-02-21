import os
import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
from helper import Helper

Helper.log("Inicio del proceso.")

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Credenciales de la base de datos
conn = {
    'SERVER': Helper.decrypt_text(os.getenv("DB_SERVER")),
    'DATABASE': Helper.decrypt_text(os.getenv("DB_NAME")),
    'UID': Helper.decrypt_text(os.getenv("DB_USER")),
    'PWD': Helper.decrypt_text(os.getenv("DB_PASSWORD")),
    'DRIVER': "ODBC Driver 17 for SQL Server"
}

# funcion para obtener los datos de Dynamics que serviran para el calculo
# EXEC dynamics.set_resumen_diario_x_item_x_tienda_petstation
def getResumenVentas():
    query = "SELECT * FROM dynamics.resumen_diario_x_item_x_tienda_petstation"
    Helper.log("Conectando a la base de datos para obtener los datos de evaluacion.")

    try:
        with pyodbc.connect('DRIVER={'+conn['DRIVER']+'};SERVER='+conn['SERVER']+';DATABASE='+conn['DATABASE']+';UID='+conn['UID']+';PWD='+conn['PWD']) as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)

        Helper.log("Datos obtenidos exitosamente.")
        return df
    
    except Exception as e:
        Helper.error(f"Error al obtener los datos: {e}")
        raise


# funcion para subir los dataframes a la base de datos
def uploadData(df, tableName):
    encoded_password = quote_plus(conn['PWD'])
    # Crear la cadena de conexión
    connection_string = 'mssql+pyodbc://'+conn['UID']+':'+encoded_password+'@'+conn['SERVER']+'/'+conn['DATABASE']+'?driver='+conn['DRIVER']
    # Crear un motor de SQLAlchemy
    engine = create_engine(connection_string)

    Helper.log(f"Subiendo los datos a la tabla {tableName}.")

    # Subir el DataFrame a SQL Server
    try:
        df.to_sql(tableName, engine, if_exists='replace', index=False)
        Helper.log(f"Datos subidos exitosamente a la tabla {tableName}.")
    except Exception as e:
        Helper.error(f"Error al subir los datos a la tabla {tableName}: {e}")
        raise


# funcion para ajustar los valores en 0
def ajuste(fila):    
    try:
        mediana = medianas.at[fila['COMBINACION'], 'CANTIDAD_VENTA']
    except:
        mediana = 0
    
    quiebre = fila['CON_QUIEBRE']
    venta = fila['CANTIDAD_VENTA']
    
    if quiebre == 0:
        r = venta
    else:
        if venta == 0:
            r = mediana
        else:
            r = venta
    
    return r


# cuenta los meses
def num_meses(x):
    return round(x.count() / 30)


# obtiene los datos para el calculo
df_pet = getResumenVentas()

Helper.log("Preparando los datos antes de la evaluacion.")

# convierte los codigos de bodega en str
df_pet['co_bodega'] = df_pet['co_bodega'].astype(str)

# crea la llave bodega-articulo
df_pet['COMBINACION'] = df_pet['co_bodega'] + '-' + df_pet['co_articulo']

# si la venta es negativa le pone 0
df_pet['CANTIDAD_VENTA'] = df_pet['CANTIDAD_VENTA'].apply(lambda x : 0 if x < 0 else x)

# ajusta las combinaciones para los productos que no tienen quiebre
sincero = df_pet[(df_pet['CON_QUIEBRE'] == 0)]

Helper.log("Calculando la media.")

# obtiene la media
medianas = sincero.groupby(by=['COMBINACION']).agg({'CANTIDAD_VENTA': 'mean'})
df_pet['AJUSTE_MEAN'] = df_pet.apply(ajuste, axis=1)

Helper.log("Calculando la mediana.")

# obtiene la mediana
medianas = sincero.groupby(by=['COMBINACION']).agg({'CANTIDAD_VENTA': 'median'})
df_pet['AJUSTE_MEDIANA'] = df_pet.apply(ajuste, axis=1)

Helper.log("Consolidando los valores calculados en la matriz producto-tienda.")

# agrupa los valores por cada combinacion existente
# venta promedio para producto - tienda
promedio = df_pet.groupby(by=['COMBINACION']).agg({
    'CANTIDAD_VENTA': 'sum',
    'AJUSTE_MEAN': 'sum',
    'AJUSTE_MEDIANA': 'sum',
    'fecha': ['count', num_meses]
}).reset_index()

# crear un nuevo dataset para el resultado
promedio.columns = [
    'COMBINACION',
    'CANTIDAD_VENTA',
    'AJUSTE_MEAN',
    'AJUSTE_MEDIANA',
    'DIAS',
    'MESES'
]

# agrega las columnas de bodega, articulo y dias para el dataset del resultado
promedio['co_bodega'] = promedio['COMBINACION'].apply(lambda x : x.split('-')[0])
promedio['co_articulo'] = promedio['COMBINACION'].apply(lambda x : x.split('-')[1])
promedio = promedio[promedio['DIAS'] > 30]

Helper.log("Consolidando los valores calculados en la matriz producto-total comercio.")

# agrupa el resultado por articulo
# venta promedio para total comercio
promedio_2 = promedio.groupby(by=['co_articulo']).agg({
    'CANTIDAD_VENTA': 'sum',
    'AJUSTE_MEAN': 'sum',
    'AJUSTE_MEDIANA': 'sum',
    'DIAS': 'max'
}).reset_index()

# agrega los valores de venta promedio para los 2 resultados
# venta promedio por producto - tienda
# venta promedio por total comercio
for i in ['CANTIDAD_VENTA', 'AJUSTE_MEAN', 'AJUSTE_MEDIANA']:
    promedio[f'{i}_prom'] = (promedio[i] / promedio['DIAS']) * 30
    promedio_2[f'{i}_prom'] = (promedio_2[i] / promedio_2['DIAS']) * 30

# exporta los resultados a CSV
Helper.log("Exportando los resultados a archivos CSV.")
promedio.to_csv('results/TiendaXProducto.csv', index=False)
promedio_2.to_csv('results/ProductoXcompania.csv', index=False)

# Sube los resultados a tablas en la base de datos
uploadData(promedio, "venta_promedio_x_item_x_bodega")
uploadData(promedio_2, "venta_promedio_x_item_x_comercio")

Helper.log("Proceso completado exitosamente.")
