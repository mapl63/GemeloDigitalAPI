from geo.tierra import es_tierra


def celda_valida_agua(grid, x, y):

    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            nx = x + dx
            ny = y + dy

            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                if grid[ny][nx] == 1:
                    return False
    return True


def encontrar_agua_cercana(grid, inicio):
    for radio in range(1, 10):
        for dx in range(-radio, radio + 1):
            for dy in range(-radio, radio + 1):

                nx = inicio[0] + dx
                ny = inicio[1] + dy

                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    if grid[ny][nx] == 0 and celda_valida_agua(grid, nx, ny):
                        return (nx, ny)
    return inicio


def suavizar_ruta(ruta, iteraciones=3):

    for _ in range(iteraciones):

        nueva = [ruta[0]]

        for i in range(1, len(ruta) - 1):
            lat = 0.25 * ruta[i - 1][0] + 0.5 * ruta[i][0] + 0.25 * ruta[i + 1][0]
            lon = 0.25 * ruta[i - 1][1] + 0.5 * ruta[i][1] + 0.25 * ruta[i + 1][1]
            nueva.append([lat, lon])

        nueva.append(ruta[-1])
        return nueva

    return ruta


def estar_cerca_tierra(lat, lon):

    for dx in [-0.003, 0, 0.003]:
        for dy in [-0.003, 0, 0.003]:
            if es_tierra(lat + dy, lon + dx):
                return True

    return False


def corregir_ruta_agua(ruta):

    ruta_corregida = []

    for lat, lon in ruta:

        if es_tierra(lat, lon) or estar_cerca_tierra(lat, lon):

            encontrado = False

            for radio in [0.005, 0.01, 0.02, 0.03]:

                for dx in [-radio, 0, radio]:
                    for dy in [-radio, 0, radio]:

                        nuevo_lat = lat + dy
                        nuevo_lon = lon + dx

                        if not es_tierra(nuevo_lat, nuevo_lon) and not estar_cerca_tierra(nuevo_lat, nuevo_lon):
                            lat = nuevo_lat
                            lon = nuevo_lon
                            encontrado = True
                            break

                    if encontrado:
                        break

        ruta_corregida.append([lat, lon])

    return ruta_corregida