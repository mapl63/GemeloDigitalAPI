import folium

def generar_mapa_ais():

    barcos = []

    with open("data/ais/ais_log.txt", "r", encoding="utf-8") as f:
        next(f)

        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            campos = linea.split(";")

            timestamp = int(campos[0])
            mmsi = int(campos[1])
            lat = float(campos[2])
            lon = float(campos[3])
            sog = float(campos[4])
            cog = float(campos[5])
            heading = int(campos[6])
            rot = int(campos[7])
            estado = int(campos[8])

            barcos.append({
                "timestamp": timestamp,
                "mmsi": mmsi,
                "lat": lat,
                "lon": lon,
                "sog": sog,
                "cog": cog,
                "heading": heading,
                "rot": rot,
                "estado": estado
            })

    if not barcos:
        raise ValueError("No hay datos AIS simulados")

    # --------------------------------------------------
    # Crear mapa centrado en el primer barco
    # --------------------------------------------------
    lat0 = barcos[0]["lat"]
    lon0 = barcos[0]["lon"]

    m = folium.Map(
        location=[lat0, lon0],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # --------------------------------------------------
    # Paleta de colores para los barcos
    # --------------------------------------------------
    colores = [
        "blue", "red", "green", "orange", "purple",
        "darkred", "cadetblue", "darkgreen", "black", "pink",
        "brown", "teal", "navy", "gold", "lime",
        "coral", "magenta", "cyan", "olive", "maroon"
    ]

    # --------------------------------------------------
    # Añadir cada barco al mapa con tooltip completo AIS
    # --------------------------------------------------
    for i, barco in enumerate(barcos):

        tooltip = (
            f"""
                <b>MMSI:</b> {barco['mmsi']}<br>
                <b>Timestamp (UTC):</b> {barco['timestamp']} s<br>
                <b>Latitud:</b> {barco['lat']:.6f}<br>
                <b>Longitud:</b> {barco['lon']:.6f}<br>
                <b>SOG:</b> {barco['sog']} nudos<br>
                <b>COG:</b> {barco['cog']}°<br>
                <b>Heading:</b> {barco['heading']}°<br>
                <b>ROT:</b> {barco['rot']}<br>
                <b>Estado navegación:</b> {barco['estado']}
            """
        )

        folium.Marker(
            location=[barco["lat"], barco["lon"]],
            tooltip=tooltip,
            icon=folium.Icon(
                icon="ship",
                prefix="fa",
                color=colores[i % len(colores)]
            )
        ).add_to(m)

    m.save("static/mapa_ais.html")