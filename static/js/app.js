// =========================
// GPS GENERAL
// =========================
const btnGpsMain = document.getElementById("btn-gps-main");
const gpsMainDiv = document.getElementById("gps-main-div");
const tituloPrincipal = document.getElementById("mostrar-titulo");


// =========================
// GPS TIEMPO REAL
// =========================
const btnGpsLive = document.getElementById("btn-gps-live");
const btnStartLive = document.getElementById("btn-start-live");
const btnStopLive = document.getElementById("btn-stop-live");
const btnVerRuta = document.getElementById("btn-ver-ruta");

const btnSetPos = document.getElementById("btn-set-pos");
const btnResetPos = document.getElementById("btn-reset-pos");

const gpsLiveDiv = document.getElementById("gps-live-div");


// =========================
// GPS A* (RUTA)
// =========================
const btnGpsAstar = document.getElementById("btn-gps-astar");
const btnCalcAstar = document.getElementById("btn-calc-astar");
const btnStartAstar = document.getElementById("btn-start-astar");
const btnStopAstar = document.getElementById("btn-stop-astar");

const gpsAstarDiv = document.getElementById("gps-astar-div");
const spinner = document.getElementById("spinner");


// =========================
// AIS
// =========================
const btnAisMain = document.getElementById("btn-ais-main");
const aisMainDiv = document.getElementById("ais-main-div");

const btnStartAis = document.getElementById("btn-start-ais");
const btnStopAis = document.getElementById("btn-stop-ais");
const btnLimpiarMapa = document.getElementById("btn-limpiar-mapa");


// =========================
// FMU
// =========================
const btnFmuMain = document.getElementById("btn-fmu-main");
const fmuMainDiv = document.getElementById("fmu-main-div");

const btnStartFmu = document.getElementById("btn-start-fmu");
const btnStopFmu = document.getElementById("btn-stop-fmu");


// =========================
// WEBSOCKET / LOADER
// =========================
const loader = document.getElementById("loader");
const loaderText = document.getElementById("loader-text");


// =========================
// CONFIG / UTILIDADES
// =========================
const coloresRutas = [
    "blue",
    "red",
    "green",
    "orange",
    "purple",
    "cyan",
    "magenta"
];

// =========================
// MARCADORES GPS 
// =========================
let barcoMarkerLive = null;
let barcoMarkerAstar = null;

let ultimaPosicion = null;
let ultimaPosicionAnterior = null;

let todasLasRutas = [];

let markerInicio = null;
let markerDestino = null;

let ultimaRuta = null;

let ultimaPosicionAstar = null; 

let modoGPS = null;

let rutaBarcoLive = null;
let rutaBarcoAstar = null;

let map = null;

let ultimoColor = null;

let rutas_acumuladas = [];

const formaBase = [0, 20, 0, -20, 0];

// =========================
// VARIABLES FMU
// =========================
let fmuData = {
    time: [],
    J1: [],
    J2: [],
    J3: [],
    J4: []
};



// =========================
// VARIABLES AIS
// =========================
let barcosAIS = {};

let aisActivo = false;
let aisConfigurado = false;

let mapaCentradoAIS = false;

// =========================
// WEST SOCKET
// =========================
const protocoloWS = window.location.protocol === "https:" ? "wss" : "ws";
const ws = new WebSocket(`${protocoloWS}://${window.location.host}/ws`);

let conectado = false;

ws.onopen = () => {
    
    conectado = true;

    loaderText.innerHTML = "✅ WebSocket conectado";

    // ✅ ESPERA VISUAL
    setTimeout(() => {
        loader.style.display = "none";
        loader.style.visibility = "hidden";
        loader.style.opacity = "0";
    }, 1000);

};

ws.onclose = () => {
    
    if(conectado) return;

    loader.style.display = "flex";
    loaderText.innerHTML = "🔄 Sin Conexión - recarga la página";

};

ws.onerror = () => {
    
    loader.style.display = "flex";
    loaderText.innerHTML = "❌ Error conectando con el servidor";

    ocultarSpinner();

};

ws.onmessage = (event) => {

    
    let data;

        try {
            data = JSON.parse(event.data);
        } catch (e) {
            console.log("IGNORADO:", event.data);
            return;
        }

    if(data.tipo === "gps"){

        console.log("GPS recibido: ", data);

            
        // 🔥 AÑADE ESTO
        if(map){
            map.invalidateSize();
        }


        ultimaPosicion = [data.lat, data.lon];
        ultimaPosicionAstar = [data.lat, data.lon];

        let colorRuta;
        

        if(data.velocidad <= 10){
            colorRuta = "lime";
        }else if(data.velocidad <= 30){
            colorRuta = "yellow";
        }else {
            colorRuta = "red";
        }

        if(modoGPS === "live" && map){
            
            const formaBase = [180, 200, 180, 160, 180];

            const nuevaForma = formaBase.map(angulo => angulo + data.rumbo);

            Plotly.update("rumbo-chart", {                  
                r: [
                    [0.0, 0.5, 0.35, 0.5, 0.0],
                    [0, 1]
                ],
                theta: [
                    nuevaForma,
                    [data.rumbo, data.rumbo]
                ]
            });

            Plotly.relayout("rumbo-chart",{
                annotations: [
                    {
                        text: data.rumbo.toFixed(0) + "°",
                        x: 0.5,
                        y: 1,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false,
                        align: "left",
                        font: { size: 26 }
                    },
                    {
                        text: "Vel: " + data.velocidad.toFixed(1) + " kn",
                        x: 0.9,
                        y: 0.77,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false,
                        font: { size: 14 }
                    },
                    {
                        text: "Lat: " + data.lat.toFixed(4),
                        x: 0.91,
                        y: 0.30,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false,
                        font: { size: 12 }
                    },
                    {
                        text: "Lon: " + data.lon.toFixed(4),
                        x: 0.9,
                        y: 0.25,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false,
                        font: { size: 12 }
                    }
                ]
            });
        }

        if(modoGPS === "live"  && document.getElementById("rumbo-chart") && window.rumboChartCreado){

            if(!barcoMarkerLive){
    
                barcoMarkerLive = L.marker([data.lat, data.lon], {
                    icon: barcoIcon(0)
                }).addTo(map)
                .bindTooltip(`
                    Punto de Partida<br>
                    Latitud: ${data.lat.toFixed(4)}<br>
                    Longitud: ${data.lon.toFixed(4)}`,
                    { permanent: true }
                );
    
                map.setView([data.lat, data.lon], 13);
    
            }else{
                barcoMarkerLive.setLatLng([data.lat, data.lon]);
                barcoMarkerLive.setIcon(barcoIcon(data.rumbo));
                barcoMarkerLive.setTooltipContent(`
                    Coordenadas<br>
                    Lat: ${data.lat.toFixed(4)}<br>
                    Lon: ${data.lon.toFixed(4)}
                    `
                );
            }
    
            if(colorRuta !== ultimoColor){

                rutaBarcoLive = L.polyline([], {
                        color: colorRuta,
                        weight: 3,
                        dashArray: "10,10"
                    }).addTo(map);
                
                rutaBarcoLive.addLatLng([data.lat, data.lon]);
                ultimoColor = colorRuta;
            }else{
                rutaBarcoLive.addLatLng([data.lat, data.lon]);
            }


        }
        
        
        if(modoGPS === "astar" && map && barcoMarkerAstar){


            barcoMarkerAstar.setLatLng([data.lat, data.lon]);
            barcoMarkerAstar.setIcon(barcoIcon(data.rumbo));

            rutaBarcoAstar.addLatLng([data.lat, data.lon]);
        }

    }

    if(data.tipo === "RUTA_COMPLETA"){
        
        const texto = document.getElementById("texto-spinner");

        if(texto){
            texto.innerHTML = "✅ Ruta calculada correctamente";
        }

        setTimeout(() => {
            ocultarSpinner();
        }, 1500);

        if(!map){
            console.log("⛔ map aún no existe → ignoro RUTA_COMPLETA");
            return;
        }

        if(!map._loaded){
            console.log("⛔ map no está listo aún");
            return;
        }

        if(!window.rutasLayerGroup){
            window.rutasLayerGroup = L.layerGroup().addTo(map);
        }

        
         // ✅ 🔥 ESTO ES LO QUE TE FALTA
        data.rutas.forEach((ruta, index) => {

            let rutaCorregida = corregirAntimeridiano(ruta);

            L.polyline(rutaCorregida, {
                color: coloresRutas[index % coloresRutas.length],
                weight: 3,
                dashArray: "20,10",
                noClip: true
            }).addTo(window.rutasLayerGroup);

        });


    }

    if(data.tipo === "fmu"){

        fmuData.time.push(data.time);
        fmuData.J1.push(data.J1_w);
        fmuData.J2.push(data.J2_w);
        fmuData.J3.push(data.J3_w);
        fmuData.J4.push(data.J4_w);

        Plotly.extendTraces("fmu-chart", {
            x: [ [data.time], [data.time], [data.time], [data.time] ],
            y: [ [data.J1_w], [data.J2_w], [data.J3_w], [data.J4_w] ]
        }, [0, 1, 2, 3]);

        const MAX_POINTS = 150;

        if(fmuData.time.length > MAX_POINTS){
            Plotly.relayout("fmu-chart", {
                xaxis: {
                    range: [
                        data.time - 15,
                        data.time
                    ]
                }
            });
        }
    }

    if(data.tipo && data.tipo.toLowerCase() === "ais"){

        console.log("AIS recibido: ", data);

        
        if(!map){
            return;
        }
        
        if(!data.barcos) return;
        
        if(!aisActivo) return;
                
        data.barcos.forEach(barco => {

            const id = barco.mmsi;
            const lat = barco.lat;
            const lon = barco.lon;
            const rumbo = barco.cog;

            if(barcosAIS[id]){

                const color = colorPorBarcoAIS(id);

                barcosAIS[id].setLatLng([lat, lon]);
                barcosAIS[id].setIcon(barcoIcon(rumbo, color));                                
                barcosAIS[id].setTooltipContent(`
                    <b>MMSI:</b> ${id}<br>
                    ${barco.nmea}
                `);



            } else {

                const color = colorPorBarcoAIS(id);

                barcosAIS[id] = L.marker([lat, lon], {
                    icon: barcoIcon(rumbo)
                })
                .addTo(map)
                .bindTooltip(`
                    <b>MMSI:</b> ${id}<br>
                    ${barco.nmea}
                `)

            }

        });


    }

    if(data.tipo === "PROGRESO_RUTA"){

        const texto = document.getElementById("texto-spinner");
        
        if(texto){
            texto.innerHTML = `Calculando ruta... ${data.progreso}%`;
        }

    }
        
    if(data.tipo === "FIN_RUTA"){
        
        const texto = document.getElementById("texto-spinner");

        if(texto){
            texto.innerHTML = "✅ Ruta calculada correctamente";
        }

        setTimeout(() => {
            ocultarSpinner();
        }, 1500);

    }


};


// =========================
// RESET GENERAL
// =========================
function ocultarTodo() {
    gpsMainDiv.classList.add("d-none");
    fmuMainDiv.classList.add("d-none");
    aisMainDiv.classList.add("d-none");

    gpsLiveDiv.classList.add("d-none");
    gpsAstarDiv.classList.add("d-none");

}

// =========================
// BOTONES PRINCIPALES
// =========================

// =========================
// BOTONES GPS
// =========================
btnSetPos.addEventListener("click", () => {

    btnStartLive.disabled = false;
    btnResetPos.classList.remove("d-none");

    const lat_fij_pos = parseFloat(document.getElementById("live-lat").value);
    const lon_fij_pos = parseFloat(document.getElementById("live-lon").value);

    ultimaPosicion = [lat_fij_pos, lon_fij_pos];

    document.getElementById("live-lat").disabled = true;
    document.getElementById("live-lon").disabled = true;


    if(map){

        if(!barcoMarkerLive){
            barcoMarkerLive = L.marker([lat_fij_pos, lon_fij_pos], {
                icon: barcoIcon(0)
            }).addTo(map);
        }else{
            barcoMarkerLive.setLatLng([lat_fij_pos, lon_fij_pos]);
        }

        
        if(!rutaBarcoLive){
            rutaBarcoLive = L.polyline([], {
                color: "green",
                weight: 3,
                dashArray: "2, 10"
            }).addTo(map);
        }


        map.setView([lat_fij_pos, lon_fij_pos], 13);
    }

    btnSetPos.innerHTML = "Posición Fijada";

    btnSetPos.disabled = true;

    document.getElementById("live-lat").disabled = true;
    document.getElementById("live-lon").disabled = true;


    console.log("Posicion Fijada", lat_fij_pos, lon_fij_pos);
});

btnResetPos.addEventListener("click", () =>{

    if(barcoMarkerLive){
        map.removeLayer(barcoMarkerLive);
        barcoMarkerLive = null;
    }

    map.eachLayer(layer => {

        if(layer instanceof L.Polyline){
            map.removeLayer(layer);
        }
    });

    ultimaPosicion = null;
    ultimaPosicionAnterior = null;

    document.getElementById("live-lat").disabled = false;
    document.getElementById("live-lon").disabled = false;

    btnSetPos.disabled = false;
    btnSetPos.innerHTML = "FIJAR POSICIÓN";

    btnResetPos.classList.add("d-none");
    btnVerRuta.classList.add("d-none");
});

btnGpsMain.addEventListener("click", () => {

    ws.send(JSON.stringify({
        tipo: "MODO",
        modo: "GPS"
    }));

    ocultarTodo();

    btnGpsMain.classList.add("btn-success");
    gpsMainDiv.classList.remove("d-none");

    
    if(!map){
        setTimeout(() => {
            initMap();
            map.invalidateSize();
        }, 100);
    } else {
        setTimeout(() => {
            map.invalidateSize()

            if(ultimaPosicion){
                map.setView(ultimaPosicion, 13);
            }

        }, 100);
    }

});

btnStartLive.addEventListener("click", () => {


    btnVerRuta.classList.remove("d-none");

    if (!ultimaPosicion){
        alert("Primero debes fijar la posición.");
        return
    }

    const lat_gps_TR = ultimaPosicion[0];
    const lon_gps_TR = ultimaPosicion[1];

    const velocidad_gps_TR = parseFloat(document.getElementById("live-vel").value);
    const rumbo_gps_TR = (parseFloat(document.getElementById("live-rumbo").value) % 360 + 360) % 360;
    document.getElementById("live-rumbo").value = rumbo_gps_TR;

    const payload = {
        tipo: "SET_POSITION",
        lat: ultimaPosicion[0],
        lon: ultimaPosicion[1],
        rumbo: rumbo_gps_TR,
        velocidad: velocidad_gps_TR
    }

    ws.send(JSON.stringify(payload));
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "START"
    }));

    btnStartLive.innerHTML = "Enviar Comando";

    console.log("Posición enviada: ", payload)

});

btnStopLive.addEventListener("click", () => {
    
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "STOP"
    }));

    console.log("Simulación detenida");
});

btnVerRuta.addEventListener("click", () => {

    fetch("/mapa/generar")
        .then(res => res.json())
        .then(data => {
            console.log("RESPUESTA MAPA:", data);

            if(data.status === "ok"){
                window.open("/mapa", "_blank");
            }else{
                alert("ERROR MAPA: " + data.detalle);
            }
        })

});

// =========================
// BOTONES GPS ASTAR
// =========================
btnCalcAstar.addEventListener("click", () => {

    mostrarSpinner();

    const startLat = parseFloat(document.getElementById("astar-start-lat").value);
    const startLon = parseFloat(document.getElementById("astar-start-lon").value);

    const endLat = parseFloat(document.getElementById("astar-end-lat").value);
    const endLon = parseFloat(document.getElementById("astar-end-lon").value);

    const vel = parseFloat(document.getElementById("astar-vel").value);

    
    // ✅ 🔥 AQUÍ VA (ESTO METELO)
    if (isNaN(vel) || vel <= 0){
        alert("Velocidad no válida");
        return;
    }


    if (isNaN(startLat) || isNaN(startLon) || isNaN(endLat) || isNaN(endLon)) {
        alert("Introduce coordenadas válidas");
        return;
    }


    // ✅ 1. Enviar posición inicial
    const payloadPos = {
        tipo: "SET_POSITION",
        lat: startLat,
        lon: startLon,
        velocidad: vel
    };

    // ✅ 2. Enviar destino (A*)
    const payloadDestino = {
        tipo: "SET_DESTINO",
        lat: endLat,
        lon: endLon,
        velocidad: vel
    };

    console.log("SET_POSITION:", payloadPos);
    console.log("SET_DESTINO:", payloadDestino);
    

    if(!window.rutasLayerGroup){
        window.rutasLayerGroup = L.layerGroup().addTo(map);
    }

    const inicio = [startLat, startLon];
    const fin = [endLat, endLon];

    ultimaPosicionAstar = inicio;

    const colorRuta = coloresRutas[todasLasRutas.length % coloresRutas.length];

    // ✅ marcador inicio (verde)
    markerInicio = L.marker(inicio, {
            icon: markerColorIcon(colorRuta)
    })
    .addTo(window.rutasLayerGroup)
    .bindTooltip(`
        Inicio<br>
        Lat: ${inicio[0].toFixed(4)}<br>
        Lon: ${inicio[1].toFixed(4)}
    `);

    
    // ✅ marcador destino (rojo)
    let destinoCorregido = corregirAntimeridiano([inicio, fin])[1];
    
    markerDestino = L.marker(destinoCorregido, {
            icon: markerColorIcon(colorRuta)
    })
    .addTo(window.rutasLayerGroup)  
    .bindTooltip(`
        Destino<br>
        Lat: ${destinoCorregido[0].toFixed(4)}<br>
        Lon: ${destinoCorregido[1].toFixed(4)}
    `);

    const bounds = L.latLngBounds([inicio, fin]);
    map.fitBounds(bounds);

    

    ws.send(JSON.stringify(payloadPos));
    ws.send(JSON.stringify(payloadDestino));

    btnStartAstar.classList.remove("d-none");

    todasLasRutas.push(colorRuta);

});

btnStartAstar.addEventListener("click", () => {

    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "START"
    }));

    modoGPS = "astar";

    
    if(!ultimaPosicionAstar){
        alert("Primero calcula la ruta");
        return;
    }

    if(!barcoMarkerAstar){
        // 🔥 CREAR SIEMPRE BIEN DESDE EL INICIO
        barcoMarkerAstar = L.marker(ultimaPosicionAstar, {
            icon: barcoIcon(0)
        }).addTo(map);
    }    

    if(!rutaBarcoAstar){
        rutaBarcoAstar = L.polyline([], {
            color: "green",
            weight: 4,
            dashArray: "10,10"
        }).addTo(map);
    }

    map.setView(ultimaPosicionAstar, 13);

    btnStopAstar.classList.remove("d-none");
    btnStartAstar.classList.add("d-none");

});


btnStopAstar.addEventListener("click", () => {
    
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "STOP"
    }));

    btnStopAstar.classList.add("d-none");
    btnStartAstar.classList.remove("d-none");
    btnStartAstar.innerHTML = "REANUDAR NAVEGACIÓN"
});

// =========================
// BOTONES FMU
// =========================
btnFmuMain.addEventListener("click", () => {

    
    ws.send(JSON.stringify({
        tipo: "MODO",
        modo: "FMU"
    }));

    ocultarTodo();

    fmuMainDiv.classList.remove("d-none");

    if(!window.fmuChartCreado){
        crearGraficaFMU();
        window.fmuChartCreado = true;
    }

    setTimeout(() => {
        const chart = document.getElementById("fmu-chart");

        Plotly.Plots.resize(chart);

        Plotly.relayout(chart, { autosize: true });
    }, 300);
});

btnStartFmu.addEventListener("click", () => {

    
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "START"
    }));


});

btnStopFmu.addEventListener("click", () => {
    
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "STOP"
    }));

    btnStartFmu.innerHTML = "▶ Reanudar FMU";

});



// =========================
// SUBMODOS GPS
// =========================
btnGpsLive.addEventListener("click", () => {

    ws.send(
        JSON.stringify({
            "tipo": "SUBMODO",
            "submodo": "GPS_LIVE" 
        })
    );

    modoGPS = "live";

    gpsLiveDiv.classList.remove("d-none");
    aisMainDiv.classList.add("d-none");

    gpsAstarDiv.classList.add("d-none");
    
    if(!window.rumboChartCreado){
        crearGraficaRumbo();
        window.rumboChartCreado = true;
    }
    
    setTimeout(() => {
            if(map){
                map.invalidateSize();
            }
        }, 100);

    tituloPrincipal.innerHTML = "SIMULACIÓN GPS EN TIEMPO REAL";

    tituloPrincipal.classList.add("titulo");    

});

btnGpsAstar.addEventListener("click", () => {

    ws.send(
        JSON.stringify({
            "tipo": "SUBMODO",
            "submodo": "GPS_ASTAR" 
        })
    );
    modoGPS = "astar";

    gpsAstarDiv.classList.remove("d-none");
    aisMainDiv.classList.add("d-none");

    gpsLiveDiv.classList.add("d-none");

    setTimeout(() => {

            // ✅ 1️⃣ limpiar marker de LIVE (para no ver doble)
            if(barcoMarkerLive){
                map.removeLayer(barcoMarkerLive);
                barcoMarkerLive = null;
            }

            if(rutaBarcoLive){
                map.removeLayer(rutaBarcoLive);
                rutaBarcoLive = null;
            }

        }, 200);

    btnStartAstar.classList.add("d-none");
    btnStopAstar.classList.add("d-none");

    tituloPrincipal.innerText = "RUTA CALCULADA";
    
    tituloPrincipal.classList.add("titulo");

});

// =========================
// SUBMODOS AIS
// =========================
btnAisMain.addEventListener("click", () => {
    
    ws.send(JSON.stringify({
        tipo: "MODO",
        modo: "AIS"
    }));

    ocultarTodo();
    
    gpsMainDiv.classList.remove("d-none");
    aisMainDiv.classList.remove("d-none");

    
    if(!map){
        setTimeout(() => {
            initMap();
            map.invalidateSize();
        }, 100);
    } else {
        setTimeout(() => map.invalidateSize(), 100);
    }

    tituloPrincipal.innerText = "SIMULACIÓN AIS";
    
    tituloPrincipal.classList.add("titulo");

});

btnStartAis.addEventListener("click", () => {

    const num = document.getElementById("numBarcos").value;
    const lat = document.getElementById("ais-lat").value;
    const lon = document.getElementById("ais-lon").value;
    const radio = document.getElementById("ais-radio").value;
   
    if (!num || !lat || !lon || !radio) {
        alert("⚠️ Rellena todos los campos antes de iniciar AIS");
        return;
    }
    
    if (num <= 0) {
        alert("⚠️ El número de barcos debe ser mayor que 0");
        return;
    }

    if (radio <= 0) {
        alert("⚠️ El radio debe ser mayor que 0");
        return;
    }
    
    // ✅ SOLO CONFIGURAR SI NO HABÍA AIS
    if (!aisConfigurado) {

        ws.send(JSON.stringify({
            tipo: "SET_AIS_CONFIG",
            num_barcos: parseInt(num),
            lat: parseFloat(lat),
            lon: parseFloat(lon),
            radio: parseFloat(radio)
        }));

        aisConfigurado = true;
        console.log("AIS configurado");

    }

    ws.send(JSON.stringify({
        tipo: "MODO",
        modo: "AIS"
    }));

    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "START"
    }));
    
    if(!mapaCentradoAIS){
        map.setView([parseFloat(lat), parseFloat(lon)], 9.4);
        mapaCentradoAIS = true;
    }

    aisActivo = true;
    console.log("▶ START AIS enviando");

});

btnStopAis.addEventListener("click", () => {
 
    ws.send(JSON.stringify({
        tipo: "CONTROL",
        accion: "STOP"
    }));

    aisActivo = false;

    btnStartAis.innerHTML = "▶ Reanudar AIS";
});

btnLimpiarMapa.addEventListener("click", limpiarMapaCompleto);


// =========================
// FUNCIONES GPS
// =========================
function barcoIcon(rumbo = 0, color = "red"){
    return L.divIcon({
        html: `<div style="
                    transform: rotate(${rumbo - 45}deg);
                    transform-origin: center;
                ">
                    <i class="fa-solid fa-location-arrow"
                       style="color:${color}; font-size:32px;">
                    </i>
               </div>`,
        className: "",
        iconSize: [32, 32]
    });
}

function crearGraficaRumbo(){
    

    const dataRumbo = [{
        type: "scatterpolar",
        
        r: [],
        theta: [],

        mode: "lines",
        fill: "toself",

        line: {
            color: "black",
            width: 2
        },
        
        fillcolor: "rgba(0, 255, 255, 0.4)"
    },{
            type: "scatterpolar",
            r: [0, 1],
            theta: [0, 0],
            mode: "lines",
            line: {
                color: "#777",
                width: 1,
                dash: "dot"
            },
            hoverinfo: "none",
        }
    ];

    const layoutRumbo = {

        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",

        margin: {
            l: 80,
            r: 80,
            t: 20,
            b: 20
        },

        polar: {
            bgcolor: "rgba(0,0,0,0)",
            radialaxis: {
                visible: false,
                range: [0, 1]
            },
            angularaxis: {
                direction: "clockwise",
                rotation: 90,
                tickmode: "array",
                tickvals: [0, 90, 180, 270],
                ticktext: ["N (0°)", "E (90°)", "S (180°)", "O (270°)"]
            }
        },
        showlegend: false,

        // 💥 AQUÍ METES TUS DATOS
        annotations: [
            {
                text: "0°",
                showarrow: false,
                font: { size: 26, color: "black" },
                x: 0.5,
                y: 1,
                xref: "paper",
                yref: "paper"
            },
            {
                text: "Vel: 0 kn",
                showarrow: false,
                font: { size: 14 },
                x: 0.79,
                y: 0.77,
                xref: "paper",
                yref: "paper"
            },
            {
                text: "Lat: ---",
                showarrow: false,
                font: { size: 12 },
                x: 0.80,
                y: 0.30,
                xref: "paper",
                yref: "paper"
            },
            {
                text: "Lon: ---",
                showarrow: false,
                font: { size: 12 },
                x: 0.80,
                y: 0.25,
                xref: "paper",
                yref: "paper"
            }
        ]
    };

    Plotly.newPlot("rumbo-chart", dataRumbo, layoutRumbo);
}

function corregirAntimeridiano(ruta) {

    const nuevaRuta = [ruta[0]];

    for (let i = 1; i < ruta.length; i++) {

        let [lat1, lon1] = nuevaRuta[nuevaRuta.length - 1];
        let [lat2, lon2] = ruta[i];

        let diff = lon2 - lon1;

        if (Math.abs(diff) > 180) {
            if (diff > 0) {
                lon2 -= 360;
            } else {
                lon2 += 360;
            }
        }

        nuevaRuta.push([lat2, lon2]);
    }

    return nuevaRuta;
}


// =========================
// FUNCION PARA CAMBIAR MAPAS
// =========================
function crearCapasBase(){

    const capaOSM = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    });

    const capaTopo = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenTopoMap"
    });

    
    const capaMarina = L.tileLayer(
        "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        {
            attribution: "© OpenSeaMap contributors",
            opacity: 0.7
        }
    );


    return{
        base: {},
        overlays: {
            "Normal": capaOSM,
            "Topográfico": capaTopo,
            "Marítimo": capaMarina
        }
    };
}

function colorAleatorio(){

    const letras = "123456789ABCDEF";

    let color = "#";

    for(let i =0; i <6; i++){
        color += letras[Math.floor(Math.random() * 16)];
    }

    return color;
}

function markerColorIcon(color){
    return L.divIcon({
        html: `<i class="fa-solid fa-location-dot"
                      style="color:${color}; font-size:28px;"></i>`,
        className: "",
        iconSize: [24, 24]
    });
}

function initMap(){

    if(map) return;

    map = L.map("mapa").setView([43.5, -8.3], 6);

    const capas = crearCapasBase();
    capas.overlays["Normal"].addTo(map);
    L.control.layers(capas.base, capas.overlays).addTo(map);

}

// =========================
// FUNCIONES FMU
// =========================
function crearGraficaFMU(){

    const data = [
        { x: [], y: [], name:"J1_w", mode: "lines", line:{color:"#00f5ff", width:2} },
        { x: [], y: [], name:"J2_w", mode: "lines", line:{color:"#ff006e", width:2} },
        { x: [], y: [], name:"J3_w", mode: "lines", line:{color:"#00ff88", width:2} },
        { x: [], y: [], name:"J4_w", mode: "lines", line:{color:"#ffd60a", width:2} }
    ];

    const layout = {

        title: {
            text: "Simulación FMU en tiempo real",
            font: { size: 20 },
            y: 0.95
        },

        autosize: true,

        paper_bgcolor: "#111",
        plot_bgcolor: "#111",

        font: {
            color: "#ffffff"
        },

        margin: {
            l: 80,
            r: 20,
            t: 80,
            b: 80
        },

        xaxis: {
            title: "Tiempo",
            gridcolor: "#333",
            zerolinecolor: "#555"
        },

        yaxis: {
            title: "Velocidad angular",
            gridcolor: "#333",
            zerolinecolor: "#555"
        },

        legend: {
            orientation: "h",
            x: 0.5,
            xanchor: "center",
            y: 1.02
        }
    };

    Plotly.newPlot("fmu-chart", data, layout, {
        displayModeBar: false,
        responsive: true
    });
}

function resetFmuChart(){

    fmuData = {
        time: [],
        J1: [],
        J2: [],
        J3: [],
        J4: []
    };

    crearGraficaFMU();
}


// =========================
// FUNCIONES AIS
// =========================
function colorPorBarcoAIS(id){
    const colores = [
        "#e74c3c",
        "#3498db",
        "#2ecc71",
        "#f1c40f",
        "#9b59b6",
        "#e67e22",
        "#1abc9c",
        "#e84393",
        "#7f8c8d",
        "#16a085"
    ];

    return colores[id % colores.length];
}

function limpiarMapaCompleto(){

    // AIS
    Object.values(barcosAIS).forEach(marker => {
        map.removeLayer(marker);
    });
    barcosAIS = {};

    // GPS LIVE
    if(barcoMarkerLive){
        map.removeLayer(barcoMarkerLive);
        barcoMarkerLive = null;
    }

    if(rutaBarcoLive){
        map.removeLayer(rutaBarcoLive);
        rutaBarcoLive = null;
    }

    // GPS ASTAR
    if(barcoMarkerAstar){
        map.removeLayer(barcoMarkerAstar);
        barcoMarkerAstar = null;
    }

    if(rutaBarcoAstar){
        map.removeLayer(rutaBarcoAstar);
        rutaBarcoAstar = null;
    }

    // Rutas A*
    if(window.rutasLayerGroup){
        window.rutasLayerGroup.clearLayers();
    }

    console.log("✅ mapa limpio manual");
}

// =========================
// FUNCIONES SPINNER
// =========================
function mostrarSpinner() {
    const texto = document.getElementById("texto-spinner");

    if(texto){
        texto.innerHTML = "Calculando ruta... 0%";
    }

    spinner.style.display = "block";
}

function ocultarSpinner() {
    spinner.style.display = "none";
}