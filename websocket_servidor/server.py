import asyncio
import duckdb
import json
import websockets
import random
import math

import time

import os

from datetime import datetime, timezone

from matriz.pathfinding import mejor_ruta
from mapa.generar_mapa_astar import generar_mapa_astar



from geo.tierra import es_tierra, actualizar_buffer_tierra
from gps.tiempo_real.utils import distancia

from gps.tiempo_real.simulacion import simulacion_gps
from gps.estatico.simulacion_astar import simulacion_gps_estatico
from fmu.simulacion_fmu import simulacion_fmu

from data.ais.simulacion_ais import simulacion_ais
from data.nmea.funciones_nmea import decimal_to_nmea, calculate_nmea_checksum

from gps.estatico.utils_astar import (
    encontrar_agua_cercana,
    suavizar_ruta,
    corregir_ruta_agua
)

# ===============================================================
# 🔹 BBDD
# ===============================================================
# Carpeta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Ruta a la base de datos
DB_PATH = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")


def get_connection():
    return duckdb.connect(DB_PATH)

con = get_connection()

con.execute("delete from estado_barco")
con.execute("delete from estado_fmu")

con.close()
# ===============================================================
# 🔹 INICIALIZACIÓN DE RECURSOS
# ===============================================================

nmea_path = os.path.join(BASE_DIR, "data", "nmea")
os.makedirs(nmea_path, exist_ok=True)

archivo_nmea = open(
    os.path.join(nmea_path, "simulacion_GPS_Estatico_nmea.txt"),
    "w",
    encoding="utf-8"
)

# ===============================================================
# 🔹 SISTEMA DE LOGS
# ===============================================================
DEBUG = True  # Cambia a False para ocultar logs DEBUG

def log(modulo, mensaje, nivel="INFO"):
    if nivel == "DEBUG" and not DEBUG:
        return
    print(f"[{nivel}] [{modulo}] {mensaje}")


# ===================================================================================
# VARIABLES GLOBALES
# ======================================================================================
# =========================
# 🔹CONTROL DEL ESTADO DEL SISTEMA
# =========================
modo_actual = None
submodo_actual = None
simulando_gps = [False]
simulando_fmu = [False]
simulando_ais = [False]
simulando_gps_estatico = [False]

clients = set()

# ==============================================================
# 🔹 CONFIGURACIÓN DE SIMULACIÓN
# ===============================================================
destino = {
    "lat" : None,
    "lon" : None,
    "velocidad" : 0.0
}

velocidad_objetivo = [0.0]

# ===============================================================
# 🔹 VARIABLES PARA AUTONAVEGACIÓN (A*)
# ===============================================================
CELL_SIZE_LAT = None
CELL_SIZE_LON = None

diff_lat = None
diff_lon = None

lat_origen = None
lon_origen = None

GRID_HEIGHT = None
GRID_WIDTH = None

waypoints = []
indice_waypoint = 0

rutas_acumuladas = []

grid_cache = None

estado_actual = {
    "timestamp" : None,
    "lat" : 43.5115,
    "lon" : -8.3316,
    "velocidad" : 1.0,
    "rumbo" : None
}

estado_fmu_actual = {
    "time" : 0.0,
    "J1_w" : 0.0,
    "J2_w" : 0.0,
    "J3_w" : 0.0,
    "J4_w" : 0.0
}

estado_ais = {}

# =======================================
# HANDLER WEBSOCKET
# =======================================
async def handler(websocket):

    global simulando_gps, simulando_fmu, simulando_ais
    global destino, velocidad_objetivo, simulando_gps_estatico
    global waypoints, indice_waypoint
    global CELL_SIZE_LAT, CELL_SIZE_LON, diff_lat, diff_lon
    global lat_origen, lon_origen
    global GRID_HEIGHT, GRID_WIDTH, rutas_acumuladas

    print("\nCliente conectado.")
    clients.add(websocket)

    # ✅ 👉 ESTA LÍNEA ES LA CLAVE
    await websocket.send_text(json.dumps({
        "tipo": "READY"
    }))

    async def keep_alive(ws):
        while True:
            try:
                await ws.ping()
            except:
                break
            await asyncio.sleep(10)


    asyncio.create_task(keep_alive(websocket))

    try:
        while True:
            message = await websocket.receive_text()

            try:
                data = json.loads(message)
            except:
                data = None

            if data and data.get("tipo") == "MODO":
                global modo_actual

                modo_actual = data.get("modo")
                print(f"Desde el frontend se ha cambiado a: {modo_actual}")
                continue

            if data and data.get("tipo") == "SUBMODO":
                global submodo_actual

                submodo_actual = data.get("submodo")

                if submodo_actual in ["GPS_ASTAR", "GPS_LIVE"]:
                    modo_actual = "GPS"

                print(f"Submodo actual cambiado a: {submodo_actual}")
                print(f"Modo ajustado automáticamente a: {modo_actual}")
                continue
            
            if data and data.get("tipo") == "CONTROL":

                accion = data.get("accion")

                if accion == "START":
                    print(f"Modo: {modo_actual} | Submodo: {submodo_actual}")

                    if modo_actual == "GPS":

                        if submodo_actual == "GPS_ASTAR":
                            simulando_gps_estatico[0] = True
                            simulando_gps[0] = False
                            simulando_fmu[0] = False
                            simulando_ais[0] = False

                            print("✅ GPS A* iniciado")

                        elif submodo_actual == "GPS_LIVE":
                            simulando_gps[0] = True
                            simulando_gps_estatico[0] = False
                            simulando_fmu[0] = False
                            simulando_ais[0] = False

                            print("✅ GPS TIEMPO REAL iniciado.")

                        else:
                            print("No hay submodo GPS seleccionado.")

                    elif modo_actual == "FMU":
                        simulando_fmu[0] = True
                        simulando_gps[0] = False
                        simulando_ais[0] = False
                        simulando_gps_estatico[0] = False
                        # estado_fmu_actual["time"] = 0.0

                        print("✅ FMU INICIADO")
                    
                    elif modo_actual == "AIS":
                        simulando_ais[0] = True
                        simulando_fmu[0] = False
                        simulando_gps[0] = False
                        simulando_gps_estatico[0] = False

                        print("✅ AIS EJECUTANDOSE")

                elif accion == "STOP":
                    simulando_gps[0] = False
                    simulando_gps_estatico[0] = False
                    simulando_fmu[0] = False
                    simulando_ais[0] = False
                    print("⛔ TODO detenido")

            elif data:

                if data.get("tipo") == "SET_POSITION":
                    estado_actual["lat"] = data["lat"]
                    estado_actual["lon"] = data["lon"]
                    
                    estado_actual["rumbo"] = data.get("rumbo", estado_actual["rumbo"])

                    if "velocidad" in data:
                        estado_actual["velocidad"] = data["velocidad"]
                        
                    estado_actual["timestamp"] = datetime.now()
                    print("Posición inicial recibida: ",
                            estado_actual["lat"],
                            estado_actual["lon"],
                            estado_actual["rumbo"],
                            )
                
                elif data.get("tipo") == "SET_DESTINO":

                    simulando_gps_estatico[0] = False

                    grid_cache = None
                    waypoints = []
                    indice_waypoint = 0

                    destino["lat"] = data["lat"]
                    destino["lon"] = data["lon"]

                    if "velocidad" in data:
                        velocidad_objetivo[0] = float(data["velocidad"])

                    print("Destino fijado: ", destino, "velocidad", velocidad_objetivo)
                        
                    if submodo_actual == "GPS_ASTAR":

                        print("Calculando ruta A-star (modo estático)")
                        inicio_total = time.perf_counter()

                        # =========================
                        # GRID DINÁMICO A*
                        # =========================
                        dist_total = distancia(
                            estado_actual["lat"],
                            estado_actual["lon"],
                            destino["lat"],
                            destino["lon"]
                        )

                        print(f"Distancia total: {dist_total:.2f} nm")

                        actualizar_buffer_tierra(dist_total)

                        es_tierra.cache_clear()
                        
                        if dist_total < 5:  # PUERTO / ZONA LOCAL
                            GRID_WIDTH = 1000
                            GRID_HEIGHT = 1000
                            print("Modo ALTA RESOLUCION (puertos)")

                        elif dist_total < 20:
                            GRID_WIDTH = 700
                            GRID_HEIGHT = 700
                            print("Modo MEDIA RESOLUCION (puertos)")
                            
                        else:
                            GRID_WIDTH = 500
                            GRID_HEIGHT = 500
                            print("Modo BAJA RESOLUCION (larga distancia)")

                        # ORIGEN REAL → (0,0) EN EL GRID
                        lat_origen = estado_actual["lat"]
                        lon_origen = estado_actual["lon"]

                        estado_actual["lat"] = lat_origen
                        estado_actual["lon"] = lon_origen

                        indice_waypoint = 0
                        
                        dest_lat = destino["lat"]
                        dest_lon = destino["lon"]

                        if abs(dest_lon - lon_origen) > 180:
                            if dest_lon < lon_origen:
                                dest_lon += 360
                            else:
                                lon_origen += 360

                        diff_lat = (dest_lat - lat_origen)
                        diff_lon = (dest_lon - lon_origen)

                        if diff_lat == 0:
                            diff_lat = 0.00001

                        if diff_lon == 0:
                            diff_lon = 0.00001
                        
                        CELL_SIZE_LAT = abs(diff_lat) / GRID_HEIGHT
                        CELL_SIZE_LON = abs(diff_lon) / GRID_WIDTH

                        
                        # ============================================
                        # ✅ MARGEN DINÁMICO SEGÚN DISTANCIA
                        # ============================================

                        if dist_total < 5:
                            margen = 0.02   # 🔥 puerto (muy preciso)
                        elif dist_total < 20:
                            margen = 0.2    # 🔥 zona costera
                        elif dist_total < 100:
                            margen = 1      # 🔥 media distancia
                        else:
                            margen = 6      # 🔥 larga distancia (como tenías antes)

                        print(f"Usando margen dinámico: {margen}")

                        lat_min = min(lat_origen, dest_lat) - margen
                        lat_max = max(lat_origen, dest_lat) + margen

                        lon_min = min(lon_origen, dest_lon) - margen
                        lon_max = max(lon_origen, dest_lon) + margen


                        # lat_min = min(lat_origen, dest_lat) - 8
                        # lat_max = max(lat_origen, dest_lat) + 8

                        # lon_min = min(lon_origen, dest_lon) - 8
                        # lon_max = max(lon_origen, dest_lon) + 8

                        if grid_cache is not None:
                            grid = grid_cache
                        else:

                            grid = []
                                                        
                            for y in range(GRID_HEIGHT):
                                if y % 5 == 0:
                                    porcentaje = int((y / GRID_HEIGHT) * 100)

                                    payload = {
                                        "tipo" : "PROGRESO_RUTA",
                                        "progreso" : porcentaje
                                    }

                                    for ws in list(clients):
                                        try:
                                            await ws.send_text(json.dumps(payload))
                                        except:
                                            clients.discard(ws)
                                    
                                    await asyncio.sleep(0)

                                    print(f"Generando la simulacion de la ruta fila {y}/{GRID_HEIGHT}")

                                fila = []

                                for x in range(GRID_WIDTH):
                                    lat = lat_min + (y / (GRID_HEIGHT - 1)) * (lat_max - lat_min)
                                    lon = lon_min + (x / (GRID_WIDTH - 1)) * (lon_max - lon_min)

                                    if es_tierra(lat, lon):
                                        fila.append(1)
                                    else:
                                        fila.append(0)

                                grid.append(fila)
                            
                            grid_cache = grid

                        # ✅ ABRIR CANAL SUPERIOR (simula Cantábrico)
                        for y in range(3):
                            for x in range(GRID_WIDTH):
                                grid[y][x] = 0

                        print("Total tierra:", sum(sum(fila) for fila in grid))
                        
                        inicio = (
                            int((lon_origen - lon_min) / (lon_max - lon_min) * (GRID_WIDTH - 1)),
                            int((lat_origen - lat_min) / (lat_max - lat_min) * (GRID_HEIGHT - 1))
                        )

                        inicio = encontrar_agua_cercana(grid, inicio)

                        destino_grid = (
                            int((dest_lon - lon_min) / (lon_max - lon_min) * (GRID_WIDTH - 1)),
                            int((dest_lat - lat_min) / (lat_max - lat_min) * (GRID_HEIGHT - 1))
                        )


                        destino_grid_x = min(destino_grid[0], GRID_WIDTH - 1)
                        destino_grid_y = min(destino_grid[1], GRID_HEIGHT - 1)

                        destino_grid = (destino_grid_x, destino_grid_y)

                        destino_grid = encontrar_agua_cercana(grid, destino_grid)
                        print("Destino grid calculado:", destino_grid)

                        grid[inicio[1]][inicio[0]] = 0
                        grid[destino_grid[1]][destino_grid[0]] = 0

                        waypoints = mejor_ruta(grid, inicio, destino_grid)
                        indice_waypoint = 0

                        print("Puntos intermedios de la Ruta: ")
                        for i, wp in enumerate(waypoints):
                            print(f" {i}: {wp}")
                                                    
                        # ============================================
                        # RUTA A* (LINEA AZUL) → ENVIAR AL FRONTEND
                        # ============================================
                        ruta_astar = []

                        punto_salida = [
                            estado_actual["lat"],
                            estado_actual["lon"]
                        ]

                        ruta_astar.append(punto_salida)

                        for wx, wy in waypoints:
                            lat = lat_min + (wy / (GRID_HEIGHT - 1)) * (lat_max - lat_min)
                            lon = lon_min + (wx / (GRID_WIDTH - 1)) * (lon_max - lon_min)
                            ruta_astar.append([lat, lon])
                        
                        ruta_astar[0] = [estado_actual["lat"], estado_actual["lon"]]
                        ruta_astar[-1] = [destino["lat"], dest_lon]

                        ruta_astar = suavizar_ruta(ruta_astar)
                        ruta_astar = corregir_ruta_agua(ruta_astar)
                                                
                        ruta_astar[-1] = [destino["lat"], destino["lon"]]

                        waypoints = ruta_astar
                        indice_waypoint = 0

                        rutas_acumuladas.append(ruta_astar)

                        print("Ruta corregida")

                        archivo = generar_mapa_astar(rutas_acumuladas)
                        print(f"Mapa A* generado: {archivo}")

                        fin_total = time.perf_counter()

                        tiempo = fin_total - inicio_total

                        minutos = int(tiempo// 60)

                        segundos = tiempo % 60

                        print(f"Tiempo total: {minutos} min {segundos:.2f} s\n")

                        payload = {
                            "tipo": "RUTA_COMPLETA",
                            "rutas": rutas_acumuladas
                        }

                        for ws in list(clients):
                            try:
                                await ws.send_text(json.dumps(payload))
                            except Exception:
                                clients.discard(ws)
                                                
                        payload = {
                            "tipo": "FIN_RUTA"
                        }

                        for ws in list(clients):
                            try:
                                await ws.send_text(json.dumps(payload))
                            except:
                                clients.discard(ws)

                elif data.get("tipo") == "SET_AIS_CONFIG":

                    global estado_ais
                    estado_ais.clear()

                    num = data.get("num_barcos", 5)
                    lat = data.get("lat")
                    lon = data.get("lon")
                    radio = data.get("radio")

                                        
                    if num is None or lat is None or lon is None or radio is None:
                            print("⚠️ Datos AIS incompletos")
                            return

                    try:
                            num = int(num)
                            lat = float(lat)
                            lon = float(lon)
                            radio = float(radio)
                    except:
                        print("⚠️ Error al convertir datos AIS")
                        return


                    

                    for i in range(num):
                        
                        mmsi = 224000000 + i

                        lat_rand = lat + random.uniform(-radio, radio)
                        lon_rand = lon + random.uniform(-radio, radio)

                        sog = random.uniform(5, 30)
                        cog = random.uniform(0, 359)

                        estado_ais[mmsi] = {
                            "mmsi": mmsi,
                            "lat": lat_rand,
                            "lon": lon_rand,
                            "sog": sog,
                            "cog": cog,
                            "heading": int(cog),
                            "rot": 0,
                            "estado_navegacion": 0,
                            "timestamp": datetime.now(timezone.utc).second
                        }

                    print(f"✅ AIS configurado → {num} barcos en ({lat}, {lon}) radio {radio}")

    except Exception as e:
        print("Cliente desconectado o error WebSocket:", e)
    
    finally:
        clients.discard(websocket)

# =========================================
async def main():
    print("Servidor WebSocket en ws://127.0.0.1:8765\n")

    fmu_task = asyncio.create_task(
        simulacion_fmu(
            estado_fmu_actual,
            clients,
            get_connection,
            simulando_fmu
        )
    )
    ais_task = asyncio.create_task(
    simulacion_ais(
        estado_ais,
        clients,
        simulando_ais
    )
)
    gps_task = asyncio.create_task(
        simulacion_gps(
            estado_actual,
            destino,
            velocidad_objetivo,
            clients,
            get_connection,
            simulando_gps
        )
    )
    gps_estatico_task = asyncio.create_task(
        simulacion_gps_estatico(
            estado_actual,
            velocidad_objetivo,
            clients,
            simulando_gps_estatico,
            waypoints,
            get_connection
        )
    )

    try:
        async with websockets.serve(handler, "0.0.0.0", 8765):
            print(f"Servidor WebSocket con simulación: {modo_actual}")
            print("Esperando conexion con cliente........")
            await asyncio.Future()

    except asyncio.CancelledError:
        pass
    
    finally:
            print("Cerrando servidor WebSocket...")
            fmu_task.cancel()
            ais_task.cancel()
            archivo_nmea.close()

            if gps_task:
                gps_task.cancel()

            if gps_estatico_task:
                gps_estatico_task.cancel()
            try:
                await gps_task
                await fmu_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    asyncio.run(main())