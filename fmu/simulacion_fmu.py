import asyncio
import math
import json


async def simulacion_fmu(
    estado_fmu_actual,
    clients,
    get_connection,
    simulando_fmu_flag
):

    dt = 0.1

    while True:

        if not simulando_fmu_flag[0]:
            await asyncio.sleep(0.1)
            continue

        estado_fmu_actual["time"] = round(
            estado_fmu_actual["time"] + dt,
            3
        )

        t = estado_fmu_actual["time"]

        estado_fmu_actual["J1_w"] = math.sin(t)
        estado_fmu_actual["J2_w"] = 0.8 * math.cos(t)
        estado_fmu_actual["J3_w"] = math.sin(0.5 * t)
        estado_fmu_actual["J4_w"] = 0.4 * math.cos(0.3 * t)

        con = get_connection()

        con.execute("""
            insert into estado_fmu (time, J1_w, J2_w, J3_w, J4_w)
            values (?, ?, ?, ?, ?)
        """, (
            estado_fmu_actual["time"],
            estado_fmu_actual["J1_w"],
            estado_fmu_actual["J2_w"],
            estado_fmu_actual["J3_w"],
            estado_fmu_actual["J4_w"]
        ))

        con.close()

        print(f"Nuevo estado FMU: {estado_fmu_actual}")

        payload = {
            "tipo": "fmu",
            "time": estado_fmu_actual["time"],
            "J1_w": estado_fmu_actual["J1_w"],
            "J2_w": estado_fmu_actual["J2_w"],
            "J3_w": estado_fmu_actual["J3_w"],
            "J4_w": estado_fmu_actual["J4_w"]
        }

        for ws in list(clients):
            try:
                await ws.send(json.dumps(payload))
            except:
                clients.discard(ws)

        await asyncio.sleep(dt)