import asyncio
import math
from datetime import datetime
import json


from gps.tiempo_real.utils import calcular_rumbo, distancia


async def simulacion_gps(
    estado_actual,
    destino,
    velocidad_objetivo,
    clients,
    get_connection,
    simulando_gps_flag
):

    while True:

        if not simulando_gps_flag[0]:
            await asyncio.sleep(0.2)
            continue

        # ---------------------------------------------
        # velocidad objetivo
        # ---------------------------------------------
        if destino["lat"] is not None:
            estado_actual["velocidad"] = velocidad_objetivo[0]

        # ---------------------------------------------
        # rumbo + distancia
        # ---------------------------------------------
        if destino["lat"] is not None and destino["lon"] is not None:

            estado_actual["rumbo"] = calcular_rumbo(
                estado_actual["lat"],
                estado_actual["lon"],
                destino["lat"],
                destino["lon"]
            )

            dist_actual = distancia(
                estado_actual["lat"],
                estado_actual["lon"],
                destino["lat"],
                destino["lon"]
            )

            if dist_actual < 0.0002:

                estado_actual["lat"] = destino["lat"]
                estado_actual["lon"] = destino["lon"]
                estado_actual["velocidad"] = 0.0

                simulando_gps_flag[0] = False
                destino["lat"] = None
                destino["lon"] = None

                print("DESTINO ALCANZADO")

                payload = {"tipo": "DESTINO_ALCANZADO"}

                for ws in list(clients):
                    try:
                        await ws.send(json.dumps(payload))
                    except:
                        clients.discard(ws)

                continue

        # ---------------------------------------------
        # movimiento
        # ---------------------------------------------
        delta = estado_actual["velocidad"] * 0.00001

        rad = math.radians(estado_actual["rumbo"])

        estado_actual["lat"] += delta * math.cos(rad)
        estado_actual["lon"] += delta * math.sin(rad)
        estado_actual["timestamp"] = datetime.now()

        # ---------------------------------------------
        # DB
        # ---------------------------------------------
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

        # ---------------------------------------------
        # WS
        # ---------------------------------------------
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