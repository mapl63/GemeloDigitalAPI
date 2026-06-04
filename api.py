from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

from websocket_servidor.server import (
    handler,
    estado_fmu_actual,
    estado_ais,
    estado_actual,
    destino,
    velocidad_objetivo,
    clients,
    get_connection as get_ws_connection,
    simulando_fmu,
    simulando_ais,
    simulando_gps,
    simulando_gps_estatico,
    waypoints
)

from fmu.simulacion_fmu import simulacion_fmu
from data.ais.simulacion_ais import simulacion_ais
from gps.tiempo_real.simulacion import simulacion_gps
from gps.estatico.simulacion_astar import simulacion_gps_estatico


from mapa.generar_mapa import generar_mapa

from mapa.generar_mapa_ais import generar_mapa_ais

from fastapi.staticfiles import StaticFiles

import duckdb
import uvicorn

import os

# Carpeta raíz del proyecto
BASE_DIR = os.path.dirname(__file__)

# Ruta a la base de datos
ruta_base_datos = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")

ultimo_mapa = None
ultimo_mapa_astar = None

def get_connection():
    return duckdb.connect(ruta_base_datos)



app = FastAPI(title="Gemelo de prueba - Barco")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

ultimo_mapa = None
ultimo_mapa_astar = None

@app.get("/")
def public():
    return RedirectResponse(url="/static/index.html")

@app.on_event("startup")
async def iniciar_tareas_websocket():
    asyncio.create_task(
        simulacion_fmu(
            estado_fmu_actual,
            clients,
            get_ws_connection,
            simulando_fmu
        )
    )

    asyncio.create_task(
        simulacion_ais(
            estado_ais,
            clients,
            simulando_ais
        )
    )

    asyncio.create_task(
        simulacion_gps(
            estado_actual,
            destino,
            velocidad_objetivo,
            clients,
            get_ws_connection,
            simulando_gps
        )
    )

    asyncio.create_task(
        simulacion_gps_estatico(
            estado_actual,
            velocidad_objetivo,
            clients,
            simulando_gps_estatico,
            waypoints,
            get_ws_connection
        )
    )

@app.get("/position/latest")
def obtener_ultima_posicion():

    con = get_connection()

    try:
        ultima_fila = con.execute("""
            SELECT timestamp, lat, lon, velocidad, rumbo
            FROM estado_barco
            ORDER BY timestamp DESC
            LIMIT 1
        """).fetchone()
    finally:
        con.close()

    if ultima_fila is None:
        return {
            "error" : "No hay datos"
        }

    timestamp, lat, lon, velocidad, rumbo = ultima_fila

    return {
        "timestamp": timestamp,
        "lat": lat,
        "lon": lon,
        "velocidad": velocidad,
        "rumbo": rumbo
    }

@app.get("/fmu")
def get_fmu():

    con = get_connection()

    try:
        filas = con.execute("""
            SELECT time, J1_w, J2_w, J3_w, J4_w
            FROM estado_fmu
            ORDER BY time
        """).fetchall()
    finally:
        con.close()

    fmu = []

    for fila in filas:
        atributos = {
            "time" : fila[0],
            "J1_w" : fila[1],
            "J2_w" : fila[2],
            "J3_w" : fila[3],
            "J4_w" : fila[4],
        }
        fmu.append(atributos)

    return {"fmu": fmu}

@app.get("/mapa/generar")
def generar_mapa_endpoint():

    global ultimo_mapa

    try:
        archivo = generar_mapa()
        ultimo_mapa = archivo
        return {
            "status" : "ok", 
            "archivo" : archivo
        }
    except Exception as e:
        return {
            "status" : "error", 
            "detalle" : str(e)
        }

@app.get("/mapa")
def mostrar_ultimo_mapa():
    if not ultimo_mapa:
        return {"error" : "No hay mapa generado todavía"}
    
    return RedirectResponse("/" +  ultimo_mapa)

@app.get("/AIS")
def mostrar_mapa_ais():
    generar_mapa_ais()
    return RedirectResponse("/static/mapa_ais.html")

@app.get("/ais/realtime")
def mostrar_mapa_ais_realtime():
    return RedirectResponse("/static/ais_realtime.html")

@app.get("/mapa_astar")
def mostrar_mapa_astar():
    return RedirectResponse("/static/mapa_astar.html")

@app.get("/exportar/csv")
def exportar_csv():

    csv_path = os.path.join(BASE_DIR, "static", "csv", "estado_barco.csv")
    csv_path = csv_path.replace("\\", "/")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)


    con = get_connection()

    try:
        con.execute(f"""
            copy(
                select
                    timestamp,
                    round(lat, 6) as Tag1,
                    round(lon, 6) as Tag2,
                    round(velocidad, 2) as Tag3,
                    round(rumbo, 2) as Tag4
                from estado_barco
                    order by timestamp asc
            )
            to '{csv_path}'
            (header, delimiter ';');
        """)
    finally:
        con.close()
    
    return RedirectResponse("/static/csv/estado_barco.csv")

@app.get("/exportar/nmea")
def exportar_nmea():

    
    nmea_path = os.path.join(BASE_DIR, "static", "nmea")
    os.makedirs(nmea_path, exist_ok=True)

    con = get_connection()

    resultado = con.execute("""
        SELECT timestamp, lat, lon
        FROM estado_barco
        ORDER BY timestamp asc
    """).fetchall()

    con.close()

    nombre_archivo = os.path.join(BASE_DIR, "static", "nmea", "posicion_barco.txt")

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:

        for fila in resultado:

            timestamp, lat, lon = fila
            hora = timestamp.strftime("%H%M%S")

            archivo.write(f"{hora},{lat},{lon}\n")

    return RedirectResponse("/static/nmea/posicion_barco.txt")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await handler(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=10000
    )