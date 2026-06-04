import os
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
from functools import lru_cache

# 🔹 Carpeta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 🔹 Ruta al shapefile
ruta = os.path.join(BASE_DIR, "websocket_servidor", "ne_land", "ne_10m_land.shp")

# 🔹 Cargar datos de tierra
land = gpd.read_file(ruta)
land = land.explode(index_parts=False)

# 🔹 Crear geometría unificada
land_union = unary_union(land.geometry)

# 🔹 Buffer inicial
land_union_buffer = land_union.buffer(0.002)


# 🔹 Función para saber si un punto es tierra
@lru_cache(maxsize=100000)
def es_tierra(lat, lon):
    lat = round(lat, 5)
    lon = round(lon, 5)
    punto = Point(lon, lat)
    return land_union_buffer.intersects(punto)


# 🔹 Ajustar buffer según distancia
def actualizar_buffer_tierra(dist_total):
    global land_union_buffer

    if dist_total < 5:
        land_union_buffer = land_union.buffer(0.0005)
    else:
        land_union_buffer = land_union.buffer(0.002)
