import duckdb
import folium
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")

def generar_mapa():
    con = duckdb.connect(DB_PATH)

    datos = con.execute("""
        select lat, lon from estado_barco
        order by timestamp
    """).fetchall()

    con.close()

    if not datos:
        raise ValueError("No hay datos de GPS")

    lat0, lon0 = datos[0]

    m = folium.Map(
        location=[lat0, lon0],
        zoom_start=13,
        tiles="OpenStreetMap"
    )

    folium.PolyLine(
        locations=datos,
        color="blue",
        weight=3,
        tooltip="Trayectoria del barco"
    ).add_to(m)

    lat_last, lon_last = datos[-1]

    folium.Marker(
        location=[lat_last, lon_last],
        tooltip=f"""
            Lat: {lat_last:.6f}<br>
            Lon: {lon_last:.6f}
        """,
        icon=folium.Icon(icon="ship", prefix="fa", color="red")
    ).add_to(m)

    output_path = os.path.join(BASE_DIR, "static", "mapa.html")
    m.save(output_path)

    return "static/mapa.html"