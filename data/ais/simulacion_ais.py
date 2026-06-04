import asyncio
import json

from data.ais.utils_ais import mover_barco_ais, ais_tipo1_to_nmea


async def simulacion_ais(
    estado_ais,
    clients,
    simulando_ais_flag
):

    while True:

        if not simulando_ais_flag[0]:
            await asyncio.sleep(1)
            continue

        barcos_payload = []

        for barco in estado_ais.values():
            mover_barco_ais(barco)
            barco["nmea"] = ais_tipo1_to_nmea(barco)
            barcos_payload.append(barco)

        payload = {
            "tipo": "ais",
            "barcos": barcos_payload
        }

        for ws in list(clients):
            try:
                await ws.send(json.dumps(payload))
            except:
                clients.discard(ws)

        await asyncio.sleep(0.1)