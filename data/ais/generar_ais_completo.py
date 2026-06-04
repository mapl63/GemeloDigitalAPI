import math
import time
import random

numero_barcos = int(input("Dime cuantos barcos quieres simular: "))

def generar_datos_ais_simulados(mmsi, lat, lon, estado_anterior=None):
    
    timestamp = int(time.time()) % 60

    if estado_anterior:
        dx = lat - estado_anterior["lat"]
        dy = lon - estado_anterior["lon"]
        sog = min(30.0, math.sqrt(dx**2 + dy**2) * 1000)
        cog = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    else:
        sog = random.uniform(0, 30)
        cog = random.uniform(0, 359)

    return {
        "tipo_mensaje": 1,
        "mmsi": mmsi,
        "lat": lat,
        "lon": lon,
        "sog": round(sog, 1),
        "cog": round(cog, 1),
        "heading": int(cog),
        "rot": 0,
        "estado_navegacion": 0,
        "timestamp": timestamp,
        "precision_posicion": 1
    }


def guardar_ais_txt(barcos):
    with open("data/ais/ais_log.txt", "w", encoding="utf-8") as f:
        f.write("timestamp;mmsi;lat;lon;sog;cog;heading;rot;estado\n")
        for barco in barcos:
            f.write(
                f"{barco['timestamp']};{barco['mmsi']};"
                f"{barco['lat']};{barco['lon']};"
                f"{barco['sog']};{barco['cog']};"
                f"{barco['heading']};{barco['rot']};"
                f"{barco['estado_navegacion']}\n"
            )


if __name__ == "__main__":
    BASE_LAT = 43.4833
    BASE_LON = -8.2369

    barcos_ais = []

    for i in range(numero_barcos):
        mmsi = 224000000 + i
        lat = BASE_LAT + random.uniform(-0.05, 0.05)
        lon = BASE_LON + random.uniform(-0.05, 0.05)

        datos_ais = generar_datos_ais_simulados(mmsi, lat, lon)
        barcos_ais.append(datos_ais)

    guardar_ais_txt(barcos_ais)
    print("AIS simulado generado en data/ais/ais_log.txt")