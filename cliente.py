import requests

API_URL = "*********"

def registrar_usuario():
    usuario = input("Ingrese su nombre de usuario: ")
    clave = input("Ingrese su clave: ")
    response = requests.post(f"{API_URL}/registro", json={"usuario": usuario, "clave": clave})
    print("Respuesta:", response.json())

def login():
    usuario = input("Usuario: ")
    clave = input("clave: ")
    response = requests.post(f"{API_URL}/login", json={"usuario": usuario, "clave": clave})
    if response.status_code == 200:
        print("Login exitoso")
        return usuario
    else:
        print("Error:", response.json())
        return None

def listar_actividades():
    response = requests.get(f"{API_URL}/actividades")
    print("\n LISTA DE ACTIVIDADES:")
    print(response.text)  # HTML simple del servidor

def crear_actividad(usuario):
    descripcion = input("Descripción de la actividad (mínimo 15 caracteres): ")
    response = requests.post(f"{API_URL}/actividades", json={"usuario": usuario, "descripcion": descripcion})
    print("Respuesta:", response.json())

def completar_actividad():
    try:
        id_actividad = int(input("ID de la actividad a marcar: "))
    except ValueError:
        print("ID inválido")
        return

    estado = input("¿Marcar como completada? (s/n): ").lower()
    completada = True if estado == "s" else False

    response = requests.put(f"{API_URL}/actividades/{id_actividad}", json={"completada": completada})
    print("Respuesta:", response.json())

def menu():
    usuario_logueado = None
    while True:
        print("\n=== GESTOR DE ACTIVIDADES ===")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Listar actividades")
        print("4. Crear actividad")
        print("5. Marcar actividad como completada/pendiente")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            usuario_logueado = login()
        elif opcion == "3":
            listar_actividades()
        elif opcion == "4":
            if usuario_logueado:
                crear_actividad(usuario_logueado)
            else:
                print("Debe iniciar sesión primero")
        elif opcion == "5":
            completar_actividad()
        elif opcion == "6":
            print("Saliendo...")
            break
        else:
            print("Opción inválida")

if __name__ == "__main__":
    menu()
