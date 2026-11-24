from datetime import datetime
from getpass import getpass

print("Fecha y hora:", datetime.now().astimezone().isoformat(timespec="seconds"))
print("Nombre completo: Johani Leandro Reyes Vasquez")

rut = getpass("Ingrese su RUT (no se mostrará mientras escribe): ").strip()
print("RUT:", rut)