from pathlib import Path

def generar_mapa_astar(rutas):

    if not rutas:
        print("Ruta vacia")
        return 

    ruta_total = []

    for i in rutas:
        ruta_total.extend(i)


    html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Ruta Global</title>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

        
        <style>
        .info-coords {{
            background: white;
            padding: 5px 10px;
            font-size: 12px;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0,0,0,0.3);
        }}
        </style>

        </head>
    <body>

        <div id="map" style="width: 100%; height: 100vh;"></div>

        <script>
            var map = L.map('map').setView({ruta_total[0]}, 3);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap'
            }}).addTo(map);

            var rutas = {rutas};
            var ruta_total = rutas.flat();
            
            rutas.forEach(function(ruta, index){{
            
                let inicio = ruta[0];
                let destino = ruta[ruta.length - 1];

                let inicioCorregido = [ inicio[0], normalizarLon(inicio[1]) ];
                let destinoCorregido = [ destino[0], normalizarLon(destino[1]) ];

                                
                

                
                L.marker(inicioCorregido)
                    .addTo(map)
                    .bindTooltip(
                        `Inicio<br>
                        Lat: ${{inicioCorregido[0].toFixed(5)}}<br>
                        Lon: ${{inicioCorregido[1].toFixed(5)}}`,
                        {{ permanent: true }}
                    )
                    .bindPopup("Inicio");

                // marcador destino
                var destinoIcon = L.divIcon({{
                    html: "📍",
                    className: "",
                    iconSize: [24, 24],
                    iconAnchor: [12,12]
                }});

                L.marker(destinoCorregido, {{ icon: destinoIcon }})
                    .addTo(map)
                    .bindTooltip(
                        `Destino<br>
                        Lat: ${{destinoCorregido[0].toFixed(5)}}<br>
                        Lon: ${{destinoCorregido[1].toFixed(5)}}`,
                        {{ permanent: true }}
                    )
                    .bindPopup("Destino");

                let segmentos = corregirAntimeridiano(ruta);

                segmentos.forEach(function(seg){{
                
                    L.polyline(seg, {{
                        color: ['red','blue','green','purple','orange'][index % 5],
                        weight: 4,
                        dashArray: '14,10'
                    }}).addTo(map);
                }});
            }});

           
            var bounds = L.latLngBounds({ruta_total});

            map.fitBounds(bounds);

            function corregirAntimeridiano(ruta) {{

                const segmentos = [];
                let segmentoActual = [];

                let prevLon = null;

                for (let i = 0; i < ruta.length; i++) {{

                    let lat = ruta[i][0];
                    let lon = ruta[i][1];

                    if (prevLon !== null) {{

                        let diff = lon - prevLon;

                        if (Math.abs(diff) > 180) {{
                            // 🔥 CORTE AQUÍ
                            segmentos.push(segmentoActual);
                            segmentoActual = [];
                        }}
                    }}

                    prevLon = lon;
                    segmentoActual.push([lat, lon]);
                }}

                if (segmentoActual.length) {{
                    segmentos.push(segmentoActual);
                }}

                return segmentos;
            }}

            function normalizarLon(lon){{
                return ((lon + 180) % 360 + 360) % 360 - 180;
            }}

            
            // crear cajita de coordenadas
            var infoCoords = L.control({{ position: 'bottomleft' }});

            infoCoords.onAdd = function () {{
                this._div = L.DomUtil.create('div', 'info-coords');
                this._div.innerHTML = "Lat: -- | Lon: --";
                return this._div;
            }};

            infoCoords.addTo(map);


            map.on('mousemove', function(e){{
                
                let lat = e.latlng.lat.toFixed(5);
                let lon = e.latlng.lng.toFixed(5);

                infoCoords._div.innerHTML = "Lat: " + lat + " | Lon: " + lon;
                
            }});



        </script>

    </body>
</html>
"""

    ruta_archivo = Path("static/mapa_astar.html")
    ruta_archivo.write_text(html, encoding="utf-8")

    return ruta_archivo.name