from datetime import datetime
from getpass import getpass

from ncclient import manager


CONFIGURACION = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname>Johani-Reyes</hostname>
    <interface>
      <Loopback>
        <name>11</name>
        <description>Examen DevNet - NETCONF</description>
        <ip>
          <address>
            <primary>
              <address>11.11.11.11</address>
              <mask>255.255.255.255</mask>
            </primary>
          </address>
        </ip>
      </Loopback>
    </interface>
  </native>
</config>
"""

FILTRO = """
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <hostname/>
  <interface>
    <Loopback>
      <name>11</name>
    </Loopback>
  </interface>
</native>
"""


def main():
    print(
        "Fecha y hora:",
        datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    clave = getpass("Contraseña del usuario devnet: ")

    with manager.connect(
        host="192.168.56.101",
        port=830,
        username="devnet",
        password=clave,
        hostkey_verify=True,
        look_for_keys=False,
        allow_agent=False,
        device_params={"name": "iosxe"},
        timeout=60,
    ) as conexion:
        print("Conexión NETCONF establecida.")
        print("ID de sesión:", conexion.session_id)

        resultado = conexion.edit_config(
            target="running",
            config=CONFIGURACION,
            default_operation="merge",
        )
        print("\nRespuesta del cambio:")
        print(resultado.xml)

        verificacion = conexion.get_config(
            source="running",
            filter=("subtree", FILTRO),
        )
        print("\nConfiguración consultada después del cambio:")
        print(verificacion.xml)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nOperación interrumpida.")
    except Exception as error:
        print("No se completó la operación.")
        print("Tipo de error:", type(error).__name__)
        print("Detalle:", error)