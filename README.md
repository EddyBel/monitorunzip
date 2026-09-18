# ZIP Extraction Monitor

Script de línea de comandos escrito en Python para **monitorear en tiempo real la extracción de un archivo ZIP**.

El script identifica automáticamente el archivo más grande dentro del ZIP y utiliza su tamaño para estimar el progreso de la descompresión, mostrando:

* Porcentaje de progreso.
* Cantidad de datos extraídos.
* Tamaño total del archivo monitoreado.
* Velocidad de extracción aproximada.
* Tiempo restante estimado.
* Detección automática de finalización.

Está pensado principalmente para archivos ZIP grandes, donde una extracción puede tardar varios minutos u horas y el sistema no proporciona información clara sobre el progreso.

---

## Características

* 🔍 Detecta automáticamente el archivo más grande dentro del ZIP.
* 📊 Muestra el progreso en tiempo real.
* ⚡ Calcula la velocidad aproximada de extracción.
* ⏱️ Calcula un tiempo restante estimado.
* 💾 Muestra los tamaños en GB y MB/s.
* 🖥️ Funciona desde la terminal.
* 🐍 No requiere dependencias externas.
* 📦 Utiliza únicamente módulos incluidos en Python.
* ⌨️ Permite detener el monitor con `Ctrl+C`.
* ✅ Verifica que el archivo proporcionado exista y sea un ZIP válido.

---

## Requisitos

Necesitas:

* Python 3.x
* Un sistema operativo con acceso a terminal.

No es necesario instalar paquetes adicionales.

El script utiliza exclusivamente módulos de la biblioteca estándar de Python:

```text
os
sys
time
zipfile
```

---

## Instalación

Puedes descargar el script directamente o clonarlo junto con el repositorio.

Por ejemplo:

```bash
git clone https://github.com/usuario/repositorio.git
cd repositorio
```

Después, asegúrate de que el archivo tenga permisos de ejecución:

```bash
chmod +x zip-monitor.py
```

También puedes ejecutarlo directamente utilizando Python:

```bash
python3 zip-monitor.py
```

---

## Uso

La sintaxis básica es:

```bash
./zip-monitor.py archivo.zip
```

O utilizando Python:

```bash
python3 zip-monitor.py archivo.zip
```

Por ejemplo:

```bash
./zip-monitor.py backup.zip
```

El script primero analiza el ZIP y encuentra el archivo más grande contenido dentro de él.

Después muestra información similar a:

```text
Analizando: backup.zip
Archivo: backup/database.sqlite
Tamaño total: 18.42 GB

 42.37% — 7.80/18.42 GB — 128.4 MB/s — faltan ~1m 23s
```

La información se actualiza aproximadamente cada segundo.

Cuando el archivo monitoreado alcanza su tamaño total:

```text
¡Descompresión terminada!
```

---

## ¿Cómo funciona?

El script **no realiza la descompresión**.

Su función es observar el archivo que está siendo creado por otro proceso de extracción.

El flujo es el siguiente:

```text
                ┌─────────────────┐
                │    archivo.zip  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Analizar ZIP    │
                │                 │
                │ Buscar archivo  │
                │ más grande      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Obtener tamaño  │
                │ total esperado  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Monitorizar     │
                │ archivo extraído│
                └────────┬────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Tamaño actual          Tiempo transcurrido
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌─────────────────┐
                │ Calcular        │
                │ progreso        │
                │ velocidad       │
                │ ETA             │
                └─────────────────┘
```

### 1. Analiza el ZIP

Utiliza `zipfile.ZipFile` para obtener todos los elementos contenidos en el archivo:

```python
with zipfile.ZipFile(zip_path) as z:
    files = [
        info
        for info in z.infolist()
        if not info.is_dir()
    ]
```

Los directorios son ignorados.

Después selecciona el archivo con mayor tamaño:

```python
max(files, key=lambda info: info.file_size)
```

Esto permite utilizar el archivo más grande como referencia del progreso.

---

### 2. Obtiene el tamaño esperado

El tamaño del archivo dentro del ZIP se obtiene mediante:

```python
info.file_size
```

Este corresponde al tamaño que tendrá el archivo una vez descomprimido.

Por ejemplo:

```text
Archivo: backup/database.sqlite
Tamaño total: 18.42 GB
```

---

### 3. Comprueba el archivo extraído

Cada segundo se comprueba si existe el archivo correspondiente:

```python
os.path.exists(filename)
```

Si existe, se obtiene su tamaño actual:

```python
os.path.getsize(filename)
```

De esta manera se puede saber aproximadamente cuánto del archivo ya ha sido escrito en disco.

---

### 4. Calcula el progreso

El porcentaje se obtiene mediante:

```text
tamaño_actual / tamaño_total × 100
```

Por ejemplo:

```text
7.80 / 18.42 × 100 = 42.34%
```

---

### 5. Calcula la velocidad

El script mide cuánto tiempo ha pasado desde que comenzó el monitor:

```python
elapsed = time.time() - start_time
```

Y utiliza el tamaño actual para calcular una velocidad aproximada:

```python
speed = current_size / elapsed
```

La velocidad se muestra en MB/s:

```text
128.4 MB/s
```

---

### 6. Estima el tiempo restante

Con la velocidad calculada y los datos que todavía faltan:

```python
remaining = (total_size - current_size) / speed
```

El resultado se convierte a un formato legible:

```text
23s
1m 42s
2h 14m
```

La estimación es aproximada y puede variar considerablemente si la velocidad de escritura cambia durante la extracción.

---

## Importante: cómo utilizarlo correctamente

El script **no inicia la extracción del ZIP**.

Primero debes iniciar la extracción utilizando otra herramienta.

Por ejemplo:

```bash
unzip backup.zip
```

Y, en otra terminal, ejecutar:

```bash
./zip-monitor.py backup.zip
```

De esta forma:

```text
Terminal 1
──────────
$ unzip backup.zip
Extracting...


Terminal 2
──────────
$ ./zip-monitor.py backup.zip

Analizando: backup.zip
Archivo: backup/database.sqlite
Tamaño total: 18.42 GB

42.37% — 7.80/18.42 GB — 128.4 MB/s — faltan ~1m 23s
```

Esto resulta especialmente útil cuando `unzip` u otra herramienta no proporciona un progreso suficientemente claro.

---

## Ejemplo completo

Supongamos que tenemos:

```text
backup.zip
```

y dentro contiene:

```text
backup/
├── config.json
├── logs/
├── database.sqlite
└── media/
```

Si `database.sqlite` es el archivo más grande:

```text
database.sqlite → 25 GB
```

el script lo seleccionará automáticamente como referencia.

Al comenzar:

```text
Analizando: backup.zip
Archivo: backup/database.sqlite
Tamaño total: 25.00 GB

  0.00% — 0.00/25.00 GB — 0.0 MB/s — faltan ~--
```

Durante la extracción:

```text
 18.52% — 4.63/25.00 GB — 142.7 MB/s — faltan ~2m 27s
```

Más adelante:

```text
 76.31% — 19.08/25.00 GB — 138.2 MB/s — faltan ~43s
```

Y finalmente:

```text
100.00% — 25.00/25.00 GB — 139.1 MB/s — faltan ~0s

¡Descompresión terminada!
```

---

## Detener el monitor

Puedes detener el script en cualquier momento utilizando:

```text
Ctrl+C
```

El script mostrará:

```text
Monitor detenido.
```

Esto **no detiene necesariamente la extracción del ZIP** que se está ejecutando en otra terminal.

Simplemente detiene el monitor.

---

## Validaciones

Antes de comenzar, el script verifica que:

### El usuario haya proporcionado un archivo

Si ejecutas:

```bash
./zip-monitor.py
```

se muestra:

```text
Uso: ./zip-monitor.py archivo.zip
```

### El archivo exista

Por ejemplo:

```bash
./zip-monitor.py inexistente.zip
```

produce:

```text
Error: no existe el archivo 'inexistente.zip'
```

### El archivo sea un ZIP válido

Si proporcionas otro tipo de archivo:

```bash
./zip-monitor.py archivo.tar
```

se mostrará:

```text
Error: 'archivo.tar' no parece ser un ZIP válido.
```

### El ZIP contenga archivos

Un ZIP que solamente contenga directorios no puede utilizarse para calcular el progreso:

```text
Error: El ZIP no contiene archivos.
```

---

## Limitaciones

El cálculo del progreso tiene algunas limitaciones importantes.

### Solo monitorea el archivo más grande

El script utiliza el archivo más grande del ZIP como referencia.

Esto significa que:

```text
archivo_A → 10 GB
archivo_B → 2 GB
archivo_C → 500 MB
```

se monitoreará:

```text
archivo_A
```

y no el progreso total de todos los archivos.

Por lo tanto, el porcentaje mostrado representa el progreso del **archivo de referencia**, no necesariamente el porcentaje exacto de toda la extracción.

---

### El nombre del archivo debe coincidir con la ruta extraída

El script obtiene el nombre almacenado dentro del ZIP:

```python
info.filename
```

y posteriormente busca ese mismo path en el sistema de archivos:

```python
os.path.exists(filename)
```

Por ello, se recomienda ejecutar el monitor desde el mismo directorio desde el cual se está realizando la extracción, especialmente cuando el ZIP contiene rutas relativas.

---

### La velocidad es aproximada

La velocidad se calcula desde el momento en que inicia el monitor.

Si comienzas a monitorear cuando la extracción ya lleva varios segundos:

```text
Extracción → ███████████░░░
Monitor     →       ↑ comienza aquí
```

el cálculo no representa la velocidad histórica completa de la extracción.

Además, cambios en:

* velocidad del disco,
* CPU,
* compresión,
* archivos pequeños,
* carga del sistema,
* caché del sistema operativo,

pueden hacer que la velocidad varíe.

---

### El ETA es una estimación

El tiempo restante se calcula suponiendo que la velocidad actual se mantiene constante.

Por ejemplo:

```text
100 MB/s → ~2 minutos
```

Si posteriormente la velocidad baja a:

```text
40 MB/s
```

el tiempo restante cambiará.

Por ello, el ETA debe considerarse una **estimación**, no un tiempo exacto.

---

## Casos de uso

Este script puede resultar especialmente útil para:

* Backups grandes.
* Imágenes de máquinas virtuales.
* Bibliotecas multimedia.
* Dumps de bases de datos.
* Backups de servidores.
* Archivos ZIP de varios GB.
* Extracciones realizadas en servidores Linux.
* Discos HDD o almacenamiento externo lento.
* Procesos donde `unzip` no proporciona una visualización clara del progreso.

---

## Estructura

El proyecto puede mantenerse extremadamente sencillo:

```text
zip-monitor/
└── zip-monitor.py
```

No requiere:

```text
requirements.txt
Docker
virtualenv
pip install
```

La única dependencia necesaria es Python 3.

---

## Licencia

Puedes adaptar esta sección según la licencia que utilice el proyecto.

Por ejemplo:

```text
MIT License
```

---

## Contribuciones

Las mejoras son bienvenidas.

Algunas posibles mejoras futuras podrían incluir:

* Progreso basado en todos los archivos del ZIP.
* Detección automática del proceso `unzip`.
* Soporte para `7z`.
* Soporte para `.tar.gz`, `.tar.xz` y otros formatos.
* Mejor cálculo de velocidad mediante ventanas móviles.
* ETA más estable.
* Colores en la terminal.
* Integración con `rich`.
* Detección automática del directorio de extracción.
* Monitoreo de múltiples archivos simultáneamente.
* Modo daemon.
* Registro de estadísticas de extracción.

---

## Licencia

Este proyecto puede distribuirse bajo los términos de la licencia que se indique en el repositorio.
