from datetime import datetime

print("Fecha y hora:", datetime.now().astimezone().isoformat(timespec="seconds"))

entrada = input("Ingrese el número de VLAN: ").strip()

try:
    vlan = int(entrada)

    if 1 <= vlan <= 1005:
        print(f"La VLAN {vlan} pertenece al rango normal.")
    elif 1006 <= vlan <= 4094:
        print(f"La VLAN {vlan} pertenece al rango extendido.")
    else:
        print(f"El valor {vlan} no corresponde a una VLAN válida.")

except ValueError:
    print("Entrada inválida: debe ingresar un número entero.")