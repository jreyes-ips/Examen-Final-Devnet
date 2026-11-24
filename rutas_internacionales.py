from datetime import datetime
from getpass import getpass

import requests


BASE_URL = "https://graphhopper.com/api/1"
PAISES = {"CL": "Chile", "AR": "Argentina"}
TRANSPORTES = {
    "1": ("Automóvil", "car"),
    "2": ("Bicicleta", "bike"),
    "3": ("A pie", "foot"),
}


def preguntar(mensaje):
    while True:
        respuesta = input(mensaje).strip()
        if respuesta.lower() == "v":
            raise SystemExit
        if respuesta:
            return respuesta
        print("Ingrese un valor o escriba v para salir.")


def consultar(servicio, parametros, clave):
    respuesta = requests.get(
        BASE_URL + servicio,
        params={**parametros, "key": clave},
        timeout=30,
    )

    try:
        datos = respuesta.json()
    except ValueError:
        raise ValueError(
            "El servidor no devolvió una respuesta JSON válida."
        ) from None

    if not respuesta.ok:
        mensaje = str(datos.get("message", "Solicitud rechazada."))
        mensaje = mensaje.replace(clave, "[CLAVE OCULTA]")
        raise ValueError(
            "Error HTTP {}: {}".format(respuesta.status_code, mensaje)
        )

    return datos


def elegir_pais():
    print("\nPaís de origen:")
    print("1. Chile")
    print("2. Argentina")

    while True:
        opcion = preguntar("Seleccione país: ")
        if opcion == "1":
            return "CL", "AR"
        if opcion == "2":
            return "AR", "CL"
        print("Seleccione 1 o 2.")


def buscar_ciudad(ciudad, pais, clave):
    datos = consultar(
        "/geocode",
        {
            "q": "{}, {}".format(ciudad, PAISES[pais]),
            "locale": "es",
            "limit": 10,
        },
        clave,
    )

    lugares = [
        lugar
        for lugar in datos.get("hits", [])
        if lugar.get("countrycode", "").upper() == pais
        and "point" in lugar
    ]

    if not lugares:
        raise ValueError(
            "No se encontraron resultados para {} en {}."
            .format(ciudad, PAISES[pais])
        )

    print("\nResultados para {}:".format(ciudad))
    for numero, lugar in enumerate(lugares, 1):
        print("{}. {}".format(numero, describir(lugar)))

    while True:
        opcion = preguntar("Seleccione el número: ")
        if opcion.isdigit() and 1 <= int(opcion) <= len(lugares):
            return lugares[int(opcion) - 1]
        print("Seleccione uno de los números mostrados.")


def describir(lugar):
    partes = []
    for campo in ("name", "city", "state", "country"):
        valor = lugar.get(campo)
        if valor and valor not in partes:
            partes.append(valor)
    return ", ".join(partes)


def elegir_transporte():
    print("\nTransporte:")
    for opcion, (nombre, perfil) in TRANSPORTES.items():
        print("{}. {}".format(opcion, nombre))

    while True:
        opcion = preguntar("Seleccione transporte: ")
        if opcion in TRANSPORTES:
            return TRANSPORTES[opcion]
        print("Seleccione 1, 2 o 3.")


def calcular_ruta(origen, destino, perfil, clave):
    punto_origen = origen["point"]
    punto_destino = destino["point"]

    datos = consultar(
        "/route",
        {
            "point": [
                "{lat},{lng}".format(**punto_origen),
                "{lat},{lng}".format(**punto_destino),
            ],
            "profile": perfil,
            "locale": "es",
            "instructions": "true",
            "calc_points": "true",
        },
        clave,
    )

    rutas = datos.get("paths", [])
    if not rutas:
        raise ValueError("No se encontró una ruta para ese transporte.")
    return rutas[0]


def mostrar_resultado(origen, destino, transporte, ruta):
    kilometros = ruta["distance"] / 1000
    millas = kilometros / 1.609344
    segundos_totales = round(ruta["time"] / 1000)
    horas, resto = divmod(segundos_totales, 3600)
    minutos, segundos = divmod(resto, 60)

    print("\n" + "=" * 65)
    print("RESULTADO DEL VIAJE")
    print(
        "Fecha y hora:",
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    print("Origen:", describir(origen))
    print("Destino:", describir(destino))
    print("Transporte:", transporte)
    print("Distancia: {:.2f} kilómetros".format(kilometros))
    print("Distancia: {:.2f} millas".format(millas))
    print(
        "Duración estimada: {} horas, {} minutos y {} segundos"
        .format(horas, minutos, segundos)
    )

    print("\nNARRATIVA DEL VIAJE")
    for numero, paso in enumerate(ruta.get("instructions", []), 1):
        print(
            "{}. {} ({:.2f} km)".format(
                numero, paso["text"], paso["distance"] / 1000
            )
        )
    print("=" * 65)


def main():
    print("RUTAS ENTRE CHILE Y ARGENTINA")
    print("Escriba v en cualquier pregunta para salir.")

    while True:
        clave = getpass("Clave API de GraphHopper (oculta): ").strip()
        if clave.lower() == "v":
            return
        if clave:
            break
        print("La clave no puede estar vacía.")

    while True:
        try:
            pais_origen, pais_destino = elegir_pais()
            ciudad_origen = preguntar(
                "\nCiudad de origen en {}: ".format(PAISES[pais_origen])
            )
            ciudad_destino = preguntar(
                "Ciudad de destino en {}: ".format(PAISES[pais_destino])
            )
            transporte, perfil = elegir_transporte()

            print("\nBuscando ciudad de origen...")
            origen = buscar_ciudad(ciudad_origen, pais_origen, clave)

            print("\nBuscando ciudad de destino...")
            destino = buscar_ciudad(ciudad_destino, pais_destino, clave)

            print("\nCalculando ruta...")
            ruta = calcular_ruta(origen, destino, perfil, clave)
            mostrar_resultado(origen, destino, transporte, ruta)

        except requests.exceptions.Timeout:
            print("La consulta superó los 30 segundos. Intente nuevamente.")
        except requests.exceptions.RequestException:
            print("No fue posible conectar. Revise Internet e intente otra vez.")
        except ValueError as error:
            print("No se pudo completar la consulta:", error)
        except (KeyError, TypeError):
            print("La respuesta del servicio no tiene el formato esperado.")


if __name__ == "__main__":
    try:
        main()
    except (SystemExit, KeyboardInterrupt, EOFError):
        pass
    finally:
        print("\nPrograma finalizado.")