import duckdb
import os
import numpy as np
import onnxruntime as rt

# Carpeta raíz
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Ruta DB
DB_PATH = os.path.join(BASE_DIR, "bbdd", "barco_gps.duckdb")

con = duckdb.connect(DB_PATH)

# Cargar modelo ONNX
model_path = os.path.join(BASE_DIR, "gps", "linear_regression.onnx")

sess = rt.InferenceSession(model_path)

entrada_name = sess.get_inputs()[0].name
salida_name = sess.get_outputs()[0].name

# Obtener datos
consulta = con.execute(
    "select velocidad from estado_barco order by timestamp desc limit 10"
).fetchdf()

X = consulta[["velocidad"]].values.astype(np.float32)

# Predicción
y_pred = sess.run(
    [salida_name],
    {entrada_name: X}
)[0]

print(y_pred)
