"""
Script simple para ejecutar pruebas de la API usando requests
No requiere psycopg2 ni conexión a base de datos
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    """Prueba básica de la API"""
    print("=" * 60)
    print("PRUEBAS DE LA API DE CITAS MÉDICAS")
    print("=" * 60)
    
    # 1. Health Check
    print("\n1️⃣  Probando Health Check del API Gateway...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Gateway está funcionando")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al API Gateway")
        print("   Asegúrate de que Docker esté corriendo: docker-compose up")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Obtener todos los pacientes
    print("\n2️⃣  Obteniendo todos los pacientes...")
    try:
        response = requests.get(f"{BASE_URL}/api/pacientes")
        if response.status_code == 200:
            pacientes = response.json()
            print(f"✅ Se encontraron {len(pacientes)} pacientes")
            if pacientes:
                print(f"   Primer paciente: {pacientes[0]['nombre']} {pacientes[0]['apellido']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Crear un nuevo paciente
    print("\n3️⃣  Creando un nuevo paciente...")
    nuevo_paciente = {
        "nombre": "Test",
        "apellido": "Usuario",
        "cedula": "9999999999",
        "fecha_nacimiento": "2000-01-01",
        "telefono": "3009999999",
        "email": "test@example.com",
        "direccion": "Calle Test 123"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            json=nuevo_paciente,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            paciente = response.json()
            paciente_id = paciente['id']
            print(f"✅ Paciente creado con ID: {paciente_id}")
            print(f"   Datos: {paciente['nombre']} {paciente['apellido']}")
            
            # 4. Obtener el paciente creado
            print(f"\n4️⃣  Obteniendo paciente con ID {paciente_id}...")
            response = requests.get(f"{BASE_URL}/api/pacientes/{paciente_id}")
            if response.status_code == 200:
                print(f"✅ Paciente encontrado: {response.json()['nombre']}")
            
            # 5. Actualizar el paciente
            print(f"\n5️⃣  Actualizando paciente con ID {paciente_id}...")
            update_data = {"telefono": "3001111111"}
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{paciente_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Paciente actualizado")
                print(f"   Nuevo teléfono: {response.json()['telefono']}")
            
            # 6. Eliminar el paciente
            print(f"\n6️⃣  Eliminando paciente con ID {paciente_id}...")
            response = requests.delete(f"{BASE_URL}/api/pacientes/{paciente_id}")
            if response.status_code == 200:
                print(f"✅ Paciente eliminado")
            
        elif response.status_code == 400:
            error_msg = response.json().get('error', 'Error desconocido')
            if 'cédula' in error_msg:
                print(f"⚠️  Paciente con esa cédula ya existe (esto es normal si ya se ejecutó el test)")
            else:
                print(f"❌ Error al crear: {error_msg}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 7. Obtener todas las citas
    print("\n7️⃣  Obteniendo todas las citas...")
    try:
        response = requests.get(f"{BASE_URL}/api/citas")
        if response.status_code == 200:
            citas = response.json()
            print(f"✅ Se encontraron {len(citas)} citas")
            if citas:
                print(f"   Primera cita: {citas[0]['especialidad']} - {citas[0]['fecha_hora']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 8. Crear una cita
    print("\n8️⃣  Creando una nueva cita...")
    nueva_cita = {
        "paciente_id": 1,
        "fecha_hora": "2025-12-25 10:00:00",
        "especialidad": "Medicina General",
        "medico": "Dr. Test",
        "motivo": "Consulta de prueba",
        "estado": "pendiente"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/citas",
            json=nueva_cita,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            cita = response.json()
            cita_id = cita['id']
            print(f"✅ Cita creada con ID: {cita_id}")
            print(f"   Especialidad: {cita['especialidad']}")
            
            # 9. Actualizar estado de la cita
            print(f"\n9️⃣  Actualizando estado de la cita {cita_id}...")
            update_data = {"estado": "confirmada"}
            response = requests.put(
                f"{BASE_URL}/api/citas/{cita_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"✅ Estado actualizado a: {response.json()['estado']}")
            
            # 10. Eliminar la cita
            print(f"\n🔟 Eliminando cita con ID {cita_id}...")
            response = requests.delete(f"{BASE_URL}/api/citas/{cita_id}")
            if response.status_code == 200:
                print(f"✅ Cita eliminada")
        else:
            print(f"❌ Error: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
