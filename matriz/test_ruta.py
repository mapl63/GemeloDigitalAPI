# test_ruta.py

from pathfinding import mejor_ruta

grid = [
    [0,0,0,0,0,1,1],
    [0,0,0,0,0,1,1],
    [0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0],
]

inicio = (0, 1)
destino = (6, 2)

ruta = mejor_ruta(grid, inicio, destino)

print("Ruta calculada:")
for paso in ruta:
    print(paso)