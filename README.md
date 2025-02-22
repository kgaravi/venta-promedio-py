# Proyecto de Cálculo de Venta Promedio

Este proyecto tiene como objetivo calcular la venta promedio de productos de inventario y subir los resultados a una base de datos.

## Estructura del Proyecto

- **Archivos principales**:
  - `calculaVentaPromedio.py`: Script principal para calcular la venta promedio.
  - `calculaVentaPromedio.ipynb`: Notebook Jupyter que realiza el mismo cálculo que `calculaVentaPromedio.py`.
  - `calculaVentaPromedioPorBodega.ipynb`: Notebook Jupyter para calcular la venta promedio por bodega específica.
  - `helper.py`: Contiene la clase `Helper` con métodos de utilidad como `decrypt_text`, `log`, y `error`.

- **Archivos de configuración**:
  - `.env`: Archivo para almacenar variables de entorno.
  - `.gitignore`: Archivo para ignorar ciertos archivos y directorios en el control de versiones.
  - `requirements.txt`: Archivo que contiene las dependencias del proyecto.
  - `README.md`: Archivo de documentación del proyecto.

- **Directorios**:
  - `results`: Directorio donde se almacenan los resultados en formato CSV.

## Instalación

1. Clona el repositorio:
    ```sh
    git clone https://github.com/tu-usuario/tu-repositorio.git
    cd tu-repositorio
    ```

2. Crea un entorno virtual y actívalo:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # En Windows
    source venv/bin/activate  # En macOS/Linux
    ```

3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

4. Crea un archivo [.env](http://_vscodecontentref_/1) en la raíz del proyecto con las siguientes variables:
    ```plaintext
    DB_SERVER=tu_servidor
    DB_NAME=tu_base_de_datos
    DB_USER=tu_usuario
    DB_PASSWORD=tu_contraseña
    ```

## Uso

### Script Principal

Para ejecutar el script principal [calculaVentaPromedio.py](http://_vscodecontentref_/2), usa el siguiente comando:
```sh
python calculaVentaPromedio.py