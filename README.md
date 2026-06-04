# 📌 Introducción
El presente proyecto consiste en el desarrollo de un sistema de simulación marítima en tiempo real basado en el concepto de gemelo digital.

La aplicación permite simular el comportamiento de embarcaciones mediante diferentes modelos de navegación, visualizar trayectorias sobre mapas interactivos, generar tráfico AIS, ejecutar simulaciones FMU y consultar los datos a través de una API REST.

El objetivo principal es proporcionar una plataforma modular capaz de representar escenarios marítimos de forma visual y en tiempo real.
# 🚀 Funcionalidades Principales

- Simulación GPS en tiempo real.
- Navegación automática mediante A*.
- Simulación AIS multibarco.
- Comunicación mediante WebSockets.
- Visualización interactiva sobre mapas.
- Simulación de modelos FMU.
- Exportación de datos CSV y NMEA.
- API REST mediante FastAPI.

La arquitectura del sistema está dividida en tres capas principales:

- Backend (Python + WebSocket + FastAPI)
- Motor de simulación
- Frontend (visualización con Leaflet y Plotly)

El sistema funciona mediante comunicación en tiempo real entre el frontend y el backend, donde se gestionan las simulaciones y los datos.


## 🔄 Flujo del sistema
```bash
[ Usuario ]
     │
     ▼
[ Frontend (HTML + JS + Plotly + Leaflet) ]
     │
     │ WebSocket (tiempo real)
     ▼
[ Servidor Python (server.py) ]
     │
     ├── Simulación GPS
     ├── Simulación AIS
     ├── Simulación FMU
     ├── Cálculo de rutas (A*)
     │
     ▼
[ Base de datos DuckDB ]
     │
     ▼
[ API REST (FastAPI) ]
     │
     ▼
[ Frontend (visualización de datos) ]
```

<br>

# Instalación
### VERSION DE PYTHON
El proyecto requiere el uso de:
```bash
Python 3.14.2
```
### 1. Creamos un entorno virtual(venv).
```bash
python -m venv venv
```

### 2. Activación del Entorno Virtual.
```bash
venv\Scripts\Activate.ps1
```
### 3.  Instalación de librerias.
```bash
pip install -r requirements.txt
```
### 4.  Ejecutar servidor websocket
```bash
python -m websocket_servidor.server
```
### 5. Abrir la API FastAPI
```bash
python api.py
```
### 6. Abrir en el navegador
```bash
http://127.0.0.1:8000
```
<br>

# 📁 Arquitectura del Proyecto

En esta sección se describe la organización actual del proyecto y la función de cada módulo principal.

```text
GemeloDigitalAPI/
├── archivos binarios/
├── bbdd/
├── csv/
├── data/
├── fmu/
├── geo/
├── gps/
├── mapa/
├── matriz/
├── static/
├── websocket_servidor/
├── websocket-cliente/
├── api.py
├── requirements.txt
└── README.md
```
---

## 🔹 archivos binarios

Contiene recursos binarios utilizados por el sistema.

Archivos incluidos:

* `CoupledClutches.fmu` → Modelo FMU utilizado para simulaciones dinámicas.
* `linear_regression.onnx` → Modelo ONNX empleado para realizar predicciones.

---

## 🔹 bbdd

Módulo encargado de la gestión de la base de datos DuckDB.

### `create_tables.py`

Inicializa la base de datos del sistema.

Funciones principales:

* Crear la base de datos.
* Crear las tablas necesarias para almacenar información GPS y FMU.

### `check_db.py`

Permite consultar y verificar la información almacenada.

Funciones principales:

* Mostrar registros almacenados.
* Exportar datos.
* Verificar el contenido de la base de datos.

### `onnx_predict.py`

Permite realizar inferencias utilizando modelos ONNX.

Funciones principales:

* Leer datos almacenados.
* Ejecutar modelos predictivos.
* Obtener resultados de inferencia.

---

## 🔹 csv

Contiene archivos CSV generados o utilizados por el sistema.

### `estado_barco.csv`

Almacena información exportada del estado de navegación.

---

## 🔹 data

Agrupa los datos utilizados por los distintos sistemas de simulación.

### ais

Contiene la lógica relacionada con la simulación AIS.

#### `generar_ais_completo.py`

Genera información AIS para múltiples embarcaciones.

#### `simulacion_ais.py`

Ejecuta simulaciones AIS en tiempo real.

#### `utils_ais.py`

Funciones auxiliares para el procesamiento de mensajes AIS.

---

### nmea

Contiene funcionalidades relacionadas con mensajes NMEA y GPS.

#### `funciones_nmea.py`

Generación y tratamiento de mensajes NMEA.

#### `posicion_barco.txt`

Archivo auxiliar para almacenar posiciones simuladas.

---

## 🔹 fmu

Módulo encargado de la simulación mediante modelos FMU.

### `simulacion_fmu.py`

Ejecuta simulaciones dinámicas utilizando modelos FMU.

Funciones principales:

* Cargar modelos FMU.
* Ejecutar simulaciones.
* Obtener resultados para su visualización.

---

## 🔹 geo

Módulo geográfico.

### `tierra.py`

Funciones relacionadas con el tratamiento de zonas terrestres utilizadas por los algoritmos de navegación.

---

## 🔹 gps

Módulo principal de simulación GPS.

### estatico

Contiene simulaciones basadas en rutas previamente calculadas.

#### `simulacion_astar.py`

Ejecuta simulaciones siguiendo rutas generadas mediante el algoritmo A*.

#### `utils_astar.py`

Funciones auxiliares utilizadas durante la simulación de rutas.

---

### tiempo_real

Contiene simulaciones GPS dinámicas.

#### `simulacion.py`

Genera posiciones GPS en tiempo real.

#### `utils.py`

Funciones de apoyo para cálculos de navegación.

---

## 🔹 mapa

Módulo encargado de la generación de mapas interactivos.

### `generar_mapa.py`

Genera mapas con la trayectoria GPS de la embarcación.

### `generar_mapa_ais.py`

Genera mapas con tráfico AIS simulado.

### `generar_mapa_astar.py`

Representa rutas calculadas mediante el algoritmo A*.

---

## 🔹 matriz

Módulo de cálculo de rutas.

### `pathfinding.py`

Implementa el algoritmo A* utilizado para la navegación.

Funciones principales:

* Cálculo de rutas óptimas.
* Movimientos diagonales.
* Penalización de zonas próximas a tierra.

### `test_ruta.py`

Archivo utilizado para validar el funcionamiento de las rutas calculadas.

---

## 🔹 static

Contiene todos los recursos del frontend.

### CSS

* `style.css`

Define el diseño visual de la aplicación.

### JavaScript

* `app.js`

Gestiona la comunicación con el backend y la actualización dinámica de la interfaz.

### HTML

* `index.html` → Página principal.
* `ais_realtime.html` → Visualización AIS en tiempo real.
* `mapa.html` → Trayectoria GPS.
* `mapa_astar.html` → Navegación mediante A*.
* `mapa_ais.html` → Visualización AIS.
* `fmu.html` → Resultados de simulaciones FMU.

---

## 🔹 websocket_servidor

Módulo encargado de la comunicación en tiempo real.

### `server.py`

Servidor WebSocket principal del sistema.

Funciones principales:

* Gestionar conexiones de clientes.
* Ejecutar simulaciones.
* Enviar datos en tiempo real.
* Coordinar GPS, AIS, FMU y navegación.

---

## 🔹 websocket-cliente

Cliente utilizado para pruebas y depuración.

### `client.py`

Permite conectarse al servidor WebSocket y verificar el intercambio de mensajes.

---

## 🔹 api.py

Punto de entrada principal de la aplicación.

Implementa una API REST mediante FastAPI.

Funciones principales:

* Consulta de posiciones GPS.
* Consulta de simulaciones FMU.
* Generación de mapas.
* Exportación de datos.
* Integración con el frontend.

✅ El sistema permite ejecutar simultáneamente:
- Simulación en tiempo real (WebSocket)
- Generación de mapas
- Exportación de datos (CSV / NMEA)
- Consultas mediante API REST


## 🧠 Gestión de concurrencia

El sistema utiliza DuckDB con apertura y cierre de conexiones por operación,
permitiendo el acceso concurrente seguro entre procesos de escritura
(simulación en tiempo real) y procesos de lectura
(API y generación de mapas) sin conflictos ni bloqueos.

# 🛠 Tecnologías Utilizadas

## Backend
- Python
- FastAPI
- WebSockets

## Bases de Datos
- DuckDB

## Simulación
- FMU
- AIS
- NMEA

## Inteligencia Artificial
- ONNX Runtime

## Frontend
- HTML5
- CSS3
- JavaScript

## Visualización
- Folium
- Leaflet
- Plotly

# TEST
## 🌍 Rutas de prueba utilizadas

Estas coordenadas se han utilizado para testear el sistema de navegación, el cálculo de rutas (A*) y la simulación GPS.

---

### 🚢 Ruta global completa (vuelta al mundo)

### 🌍 🇪🇸 Europa

#### Origen – Galicia (España)
- 43.5115  
- -8.3316  


#### Barcelona (Mediterráneo)
- 41.3851  
- 2.1734  

---

### 🌊 Atlántico

#### Canarias
- 28.1000  
- -15.4000  

#### Cabo Verde
- 15.1000  
- -23.6000  

---

### 🌍 África

#### São Tomé
- 0.3365  
- 6.7273  

#### Ciudad del Cabo (Sudáfrica)
- -33.9249  
- 18.4241  

---

### 🌏 Asia

#### Sri Lanka
- 7.8731  
- 80.7718  

###  Australia Occidental
- -33.3271
- 115.6414

### Japón (costa suroeste - Kyushu)
- 31.5966
- 130.5571

### 🌏 Pacífico Norte 

#### Rusia (Petropavlovsk-Kamchatsky)
- 52.93
- 158.78

#### Estados Unidos (Los Ángeles)
- 34.0522
- -118.2437

---
### 🌎 América del Sur (Costa Pacífico)

#### Perú (Lima)
- -12.0464  
- -77.0428  

#### Punto sur extremo
- -55.9690  
- -67.2600  

---

### 🇦🇷 Atlántico Sur

#### Argentina (Buenos Aires)
- -34.6037  
- -58.3816  

### 🌎 Subida por Atlántico

#### Brasil (Río de Janeiro)
- -22.9068  
- -43.1729 

## Coordenadas del puerto (muelle)
- -3.7225
- -38.4680

### Georgetown (Guyana) – costa
- 6.80
- -58.16

### 🇺🇸 Costa Este USA

#### Nueva York
- 40.7128  
- -74.0060  

### 🌊 Regreso a Europa

#### Azores (Portugal)
- 37.7412  
- -25.6756  

---

### 📍 Destino final

#### Galicia (España)
- 43.5115  
- -8.3316
--- 

### Canarias (tests específicos Iniciar Navegación) 

#### La Gomera
- 28.0916  
- -17.1110  

#### Santa Cruz de Tenerife
- 28.4762  
- -16.2246  

#### Punto adicional
- 28.1009  
- -15.6989

# 👨‍💻 Autor

Marius Puruguay López

Proyecto desarrollado durante las prácticas del ciclo formativo de Desarrollo de Aplicaciones Web (DAW) realizadas en Navantia.

Tecnologías principales:
- Python
- FastAPI
- DuckDB
- WebSockets
- Folium
- Plotly
- ONNX
- FMU#   G e m e l o D i g i t a l A P I  
 