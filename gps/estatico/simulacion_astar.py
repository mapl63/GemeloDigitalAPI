import asyncio
import math
from datetime import datetime
import json

from gps.tiempo_real.utils import calcular_rumbo, distancia


async def simulacion_gps_estatico(
    estado_actual,
    velocidad_objetivo,
    clients,
    simulando_gps_estatico_flag,
    waypoints,
    get_connection
):

    indice_waypoint = 0

    while True:

        if not simulando_gps_estatico_flag[0]:
            await asyncio.sleep(0.01)
            continue

        if not waypoints:
            simulando_gps_estatico_flag[0] = False
            print("No hay waypoints")
            continue

        if indice_waypoint >= len(waypoints):
            simulando_gps_estatico_flag[0] = False
            continue

        wp_lat, wp_lon = waypoints[indice_waypoint]

        dist = distancia(
            estado_actual["lat"],
            estado_actual["lon"],
            wp_lat,
            wp_lon
        )

        dist_antes = dist

        estado_actual["rumbo"] = calcular_rumbo(
            estado_actual["lat"],
            estado_actual["lon"],
            wp_lat,
            wp_lon
        )

        estado_actual["velocidad"] = velocidad_objetivo[0]

        delta = estado_actual["velocidad"] * 0.00001

        umbral = max(0.04, delta * 2.5)

        if dist < umbral:

            print(f"Waypoint {indice_waypoint} alcanzado")

            indice_waypoint += 1

            if indice_waypoint >= len(waypoints):

                simulando_gps_estatico_flag[0] = False
                print("Destino ALCANZADO")

                payload = {"tipo": "DESTINO_ALCANZADO"}

                for ws in list(clients):
                    try:
                        await ws.send(json.dumps(payload))
                    except:
                        clients.discard(ws)

            continue

        rad = math.radians(estado_actual["rumbo"])

        estado_actual["lat"] += delta * math.cos(rad)
        estado_actual["lon"] += delta * math.sin(rad)
        estado_actual["timestamp"] = datetime.now()

        con = get_connection()

        con.execute("""
            insert into estado_barco (timestamp, lat, lon, velocidad, rumbo)
            values (?, ?, ?, ?, ?)
        """, (
            estado_actual["timestamp"],
            estado_actual["lat"],
            estado_actual["lon"],
            estado_actual["velocidad"],
            estado_actual["rumbo"]
        ))

        con.close()

        payload = {
            "tipo": "gps",
            "timestamp": str(estado_actual["timestamp"]),
            "lat": estado_actual["lat"],
            "lon": estado_actual["lon"],
            "velocidad": estado_actual["velocidad"],
            "rumbo": estado_actual["rumbo"]
        }

        for ws in list(clients):
            try:
                await ws.send(json.dumps(payload))
            except:
                clients.discard(ws)

        await asyncio.sleep(1)
