import asyncio
import websockets
import json

async def main():
    uri = "ws://127.0.0.1:8765"

    print("\nConectando al servidor WebSocket...")

    async with websockets.connect(uri) as websocket:
        print("Conectado al servidor")
        print("-" * 40)

        # ----- Pedir datos GPS-----
        await websocket.send("GET_GPS")
        print("Petición GET_GPS enviada\n")

        response_gps = await websocket.recv()
        data_gps = json.loads(response_gps)
        print("Respuesta GPS recibida: ")
        print(data_gps)

        # ----- Pedir datos FMU ----
        print("-" * 40 + "\n")
        await websocket.send("GET_FMU")
        print("Petición GET_FMU enviada\n")

        response_fmu = await websocket.recv()
        data_fmu = json.loads(response_fmu)

        print("Respuesta FMU recibida:")
        print(data_fmu)

if __name__ == "__main__":
    asyncio.run(main())