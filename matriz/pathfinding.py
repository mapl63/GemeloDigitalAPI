import heapq
import math

def mover_celda(pos, grid):
    x, y = pos
    
    movimientos = [
        (-1,0), (1,0), (0,-1), (0,1),   # cardinales
        (-1,-1), (-1,1), (1,-1), (1,1)  # diagonales ✅
    ]

    for dx, dy in movimientos:
        nx = x + dx 
        ny = y + dy

        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
            if grid[ny][nx] != 1:

                if dx != 0 and dy != 0:
                    if grid[y][nx] == 1 or grid[ny][x] == 1:
                        continue

                yield (nx, ny, dx, dy)

def heuristica(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def mejor_ruta(grid, inicio, destino):

    cola = []
    heapq.heappush(cola, (0, inicio))

    # diccionario para guardar de donde viene cada nodo 
    came_from = {}

    distancia_recorrida = {inicio : 0}

    visitados = set()

    while cola:

        _, actual = heapq.heappop(cola)

        if actual in visitados:
            continue

        visitados.add(actual)

        if actual == destino:
            break

        for v in mover_celda(actual, grid):
            x, y, dx, dy = v

            nodo = (x,y)
            
            if dx != 0 and dy != 0:
                coste = 1.4
            else:
                coste = 1.0
            
            
            cerca = any(
                0 <= y + dy2 < len(grid) and
                0 <= x + dx2 < len(grid[0]) and
                grid[y + dy2][x + dx2] == 1
                for dx2 in [-2, -1, 0, 1, 2]
                for dy2 in [-2, -1, 0, 1, 2]
            )


            if cerca:
                coste += 3

            dx_dest = destino[0] - actual[0]
            dy_dest = destino[1] - actual[1]

            dx_move = x - actual[0]
            dy_move = y - actual[1]

            producto = dx_dest * dx_move + dy_dest * dy_move

            if producto < 0:
                coste += 0.5
            
            
            numero_pasos = distancia_recorrida[actual] + coste
            
            if nodo not in distancia_recorrida or numero_pasos < distancia_recorrida[nodo]:
                distancia_recorrida[nodo] = numero_pasos
                prioridad = numero_pasos + heuristica(nodo, destino)
                heapq.heappush(cola, (prioridad, nodo))
                came_from[nodo] = actual
    
    ruta = []
    actual = destino

    while actual != inicio:
        ruta.append(actual)
        actual = came_from.get(actual)

        if actual is None:
            return []
    
    ruta.append(inicio)

    return ruta[::-1]