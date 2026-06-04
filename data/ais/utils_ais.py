import random
import math
from datetime import datetime, timezone


def mover_barco_ais(barco):

    cog_anterior = barco["cog"]

    barco["cog"] = (barco["cog"] + random.uniform(-2, 2)) % 360
    barco["sog"] = max(0, min(barco["sog"] + random.uniform(-0.2, 0.2), 30))

    delta = barco["sog"] * 0.00001
    rad = math.radians(barco["cog"])

    barco["lat"] += delta * math.cos(rad)
    barco["lon"] += delta * math.sin(rad)

    barco["heading"] = int(barco["cog"])
    barco["timestamp"] = datetime.now(timezone.utc).second

    dt = 0.1
    diff = (barco["cog"] - cog_anterior + 180) % 360 - 180
    barco["rot"] = round(diff / dt, 2)


def ais_tipo1_to_nmea(barco):
    return (
        f"<b>Timestamp (UTC):</b> {barco.get('timestamp', '-')} s<br>"
        f"<b>Latitud:</b> {barco.get('lat', '-'):.6f}<br>"
        f"<b>Longitud:</b> {barco.get('lon', '-'):.6f}<br>"
        f"<b>SOG:</b> {barco.get('sog', '-'):.1f} nudos<br>"
        f"<b>COG:</b> {barco.get('cog', '-'):.1f}°<br>"
        f"<b>Heading:</b> {barco.get('heading', '-')}°<br>"
        f"<b>ROT:</b> {barco.get('rot', 0)}<br>"
        f"<b>Estado navegación:</b> {barco.get('estado_navegacion', 0)}"
    )