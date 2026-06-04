
import duckdb
import os

# Carpeta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Ruta a la base de datos
DB_PATH = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")

# Ruta del CSV local
csv_path = os.path.join(BASE_DIR, "csv", "estado_barco.csv")

# Ruta del CSV para la web
csv_web_path = os.path.join(BASE_DIR, "static", "csv", "estado_barco.csv")

#Conexión con la base de datos
con = duckdb.connect(DB_PATH)

# =========================
# GPS DATOS
# =========================
resultado = con.execute("""
    SELECT timestamp, lat, lon, velocidad, rumbo
        FROM estado_barco
        ORDER BY timestamp asc
""").fetchall()

print("Datos del barco: ")

posicion = 0

for fila in resultado:
    print(f"""    
Posición {posicion} del Barco.
    Fecha/Hora = {fila[0]}
        Latitud = {fila[1]:.6f}
        Longitud = {fila[2]:.6f}
        Velocidad = {fila[3]:.6f}
        Rumbo = {fila[4]:.2f}
    """
    )
    posicion += 1

# =========================
# EXPORTAR A CSV
# =========================
os.makedirs("csv", exist_ok=True)
os.makedirs("static/csv", exist_ok=True)


con.execute(f"""
    copy(
        select 
            timestamp, 
            round(lat, 6) as Tag1,
            round(lon, 6) as Tag2, 
            Round(velocidad, 2) as Tag3, 
            round(rumbo, 2) as Tag4
        from estado_barco
        order by timestamp asc
    )
    to '{csv_path}'
    (header, delimiter ';');
""")


# ✅ copia WEB
con.execute(f"""
    copy(
        select 
            timestamp, 
            round(lat, 6),
            round(lon, 6), 
            round(velocidad, 2), 
            round(rumbo, 2)
        from estado_barco
        order by timestamp asc
    )
    to '{csv_web_path}'
    (header, delimiter ';');
""")


print("Archivo CSV generado: estado_barco.csv\n")
con.close()


# =============================
# Crear NMEA
# =============================
def calculate_nmea_checksum(sentence):
    data = sentence.split('*')[0][1:]
    
    checksum = 0

    for char in data:
        checksum ^= ord(char)
    
    return '{:02X}'.format(checksum)


def decimal_to_nmea(coord, is_lat):

    cordenadas = abs(coord)
    
    grados = int(cordenadas)
    
    minutes = (cordenadas - grados) * 60

    if is_lat:
        if coord >= 0:
            hemi = 'N' 
        else: 
            hemi = 'S'
        return f"{grados:02d}{minutes:07.4f}", hemi
    else:
        if coord >= 0: 
            hemi = 'E' 
        else:
            hemi = 'W'
        return f"{grados:03d}{minutes:07.4f}", hemi


os.makedirs("static/nmea", exist_ok=True)
os.makedirs("data/nmea", exist_ok=True)

nombre_archivo = f"data/nmea/posicion_barco.txt"
nombre_archivo_web = f"static/nmea/posicion_barco.txt"

with open(nombre_archivo, "w", encoding="utf-8") as archivo_local,\
     open(nombre_archivo_web, "w", encoding="utf-8") as archivo_web:

    for fila in resultado:

        timestamp = fila[0]
        lat = fila[1]
        lon = fila[2]

        gps_valido = lat is not None and lon is not None

        if gps_valido:
            status = "A"
        else:
            status = "V"

        hora = timestamp.strftime("%H%M%S")
        lat_nmea, lat_hemi = decimal_to_nmea(lat, True)
        lon_nmea, lon_hemi = decimal_to_nmea(lon, False)
        
        nmea_base = f"$GPGLL,{lat_nmea},{lat_hemi},{lon_nmea},{lon_hemi},{hora},{status},A*"

        checksum = calculate_nmea_checksum(nmea_base)

        nmea_final = nmea_base + checksum

        archivo_local.write(f"{nmea_final}\n")
        archivo_web.write(f"{nmea_final}\n")

print(f"Archivo NMEA generado: {nombre_archivo}\n")