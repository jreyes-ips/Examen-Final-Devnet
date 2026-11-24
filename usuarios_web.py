import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

BASE_DATOS = Path(__file__).resolve().parent / "usuarios.db"


def fecha_actual():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def conectar():
    conexion = sqlite3.connect(str(BASE_DATOS))
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar():
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL
            )
        """)


@app.route("/", methods=["GET"])
def inicio():
    return """
    <!doctype html>
    <html lang="es">
    <head><meta charset="utf-8"><title>Usuarios DevNet</title></head>
    <body>
        <h1>Gestión de usuarios — Examen DevNet</h1>
        <p>Johani Leandro Reyes Vasquez</p>
        <p>Aplicación disponible en el puerto 5800.</p>
        <p>Registro: POST /registro</p>
        <p>Validación: POST /login</p>
        <p>Los usuarios se almacenan en SQLite con hashes de contraseña.</p>
    </body>
    </html>
    """


@app.route("/registro", methods=["POST"])
def registrar():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "")

    if not usuario or not password:
        return jsonify(
            mensaje="Debe ingresar usuario y contraseña.",
            fecha=fecha_actual(),
        ), 400

    if len(usuario) > 80 or len(password) < 8:
        return jsonify(
            mensaje="Usuario: máximo 80 caracteres. Contraseña: mínimo 8.",
            fecha=fecha_actual(),
        ), 400

    password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256:600000",
        salt_length=16,
    )

    try:
        with conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO usuarios
                    (usuario, password_hash, fecha_creacion)
                VALUES (?, ?, ?)
                """,
                (usuario, password_hash, fecha_actual()),
            )
    except sqlite3.IntegrityError:
        return jsonify(
            mensaje="El usuario ya existe.",
            fecha=fecha_actual(),
        ), 409

    return jsonify(
        mensaje="Usuario registrado correctamente.",
        usuario=usuario,
        fecha=fecha_actual(),
    ), 201


@app.route("/login", methods=["POST"])
def validar():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "")

    if not usuario or not password:
        return jsonify(
            mensaje="Debe ingresar usuario y contraseña.",
            fecha=fecha_actual(),
        ), 400

    with conectar() as conexion:
        registro = conexion.execute(
            "SELECT password_hash FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()

    if registro and check_password_hash(registro["password_hash"], password):
        return jsonify(
            mensaje="Autenticación correcta.",
            usuario=usuario,
            fecha=fecha_actual(),
        ), 200

    return jsonify(
        mensaje="Usuario o contraseña incorrectos.",
        fecha=fecha_actual(),
    ), 401


if __name__ == "__main__":
    inicializar()
    print("Fecha y hora:", fecha_actual())
    print("Base de datos:", BASE_DATOS)
    print("Abra http://127.0.0.1:5800")
    app.run(host="127.0.0.1", port=5800, debug=False)