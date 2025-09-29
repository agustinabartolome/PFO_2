from flask import Flask, request, jsonify, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)

def init_db():
    """Crear las tablas de usuarios y actividades"""
    with sqlite3.connect("actividades.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            descripcion TEXT NOT NULL,
            completada INTEGER DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
        """)
        conn.commit()

def get_user_by_username(username):
    """Devuelve usuario según su nombre"""
    with sqlite3.connect("actividades.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (username,))
        return cursor.fetchone()

# Endpoints

@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Deben completarse ambos campos"}), 400

    usuario = data.get("usuario", "").strip()
    clave = data.get("clave", "").strip()

    if not usuario or not clave:
        return jsonify({"error": "Se requiere usuario y clave"}), 400

    if len(usuario) < 6:
        return jsonify({"error": "El usuario debe tener al menos seis caracteres"}), 400

    if len(clave) < 8:
        return jsonify({"error": "La clave debe tener al menos ocho caracteres"}), 400

    if not re.match(r"^[A-Za-z0-9_]+$", usuario):
        return jsonify({"error": "El usuario solo puede contener letras, números y guiones bajos"}), 400

    hashed_pw = generate_password_hash(clave)

    try:
        with sqlite3.connect("actividades.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, clave) VALUES (?, ?)", (usuario, hashed_pw))
            conn.commit()
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El usuario ya existe"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Deben completarse ambos campos"}), 400

    usuario = data.get("usuario", "").strip()
    clave = data.get("clave", "").strip()

    if not usuario or not clave:
        return jsonify({"error": "Se requiere usuario y clave"}), 400

    user = get_user_by_username(usuario)
    if user and check_password_hash(user[2], clave):
        return jsonify({"mensaje": f"Login exitoso. Bienvenido {usuario}"}), 200
    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route("/actividades", methods=["GET", "POST"])
def actividades():
    if request.method == "GET":
        with sqlite3.connect("actividades.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, descripcion, completada FROM actividades")
            actividades = cursor.fetchall()

        if not actividades:
            return "<h2>No hay actividades registradas</h2>"

        html = """
        <h1>Gestor de Actividades</h1>
        <ul>
        {% for t in actividades %}
            <li>ID {{ t[0] }} - {{ t[1] }} - {% if t[2]==1 %} Completada {% else %} Pendiente {% endif %}</li>
        {% endfor %}
        </ul>
        """
        return render_template_string(html, actividades=actividades)

    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Deben completarse ambos campos"}), 400

        usuario = data.get("usuario", "").strip()
        descripcion = data.get("descripcion", "").strip()

        if not usuario or not descripcion:
            return jsonify({"error": "Usuario y descripción requeridos"}), 400

        if len(descripcion) < 15:
            return jsonify({"error": "La descripción debe tener al menos 15 caracteres"}), 400

        user = get_user_by_username(usuario)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        with sqlite3.connect("actividades.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO actividades (usuario_id, descripcion) VALUES (?, ?)", (user[0], descripcion))
            conn.commit()
        return jsonify({"mensaje": "Actividad creada con éxito"}), 201

@app.route("/actividades/<int:id>", methods=["PUT"])
def completar_actividad(id):
    data = request.get_json()
    if not data or "completada" not in data:
        return jsonify({"error": "Se requiere el campo 'completada'"}), 400

    completada = 1 if data["completada"] else 0

    with sqlite3.connect("actividades.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE actividades SET completada=? WHERE id=?", (completada, id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Actividad no encontrada"}), 404
        conn.commit()

    return jsonify({"mensaje": f"Actividad {'completada' if completada else 'marcada como pendiente'}"}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False)  
