import duckdb
import os


# Carpeta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Ruta a la base de datos
DB_PATH = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")

con = duckdb.connect(DB_PATH)

# =========================
# Crear tabla GPS
# =========================
con.execute("""
create table if not exists estado_barco(
    timestamp timestamp,
    lat double,
    lon double,
    velocidad double,
    rumbo double
)
""")

print("Base de datos GPS creada correctamente.")

# =========================
# Crear tabla FMU
# =========================
con.execute("""
    create table if not exists estado_fmu(
        time double,
        J1_w double,
        J2_w double,
        J3_w double,
        J4_w double
    )
""")

print("Tabla de estado FMU creada correctamente.")

con.close()
