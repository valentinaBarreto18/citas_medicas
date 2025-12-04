import pytest
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio del servicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Paciente

@pytest.fixture
def client():
    """Cliente de prueba para Flask"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def sample_paciente():
    """Datos de ejemplo para un paciente"""
    return {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'cedula': '1234567890',
        'fecha_nacimiento': '1990-05-15',
        'telefono': '3001234567',
        'email': 'juan.perez@email.com',
        'direccion': 'Calle 123 #45-67'
    }

def test_health_check(client):
    """Test del endpoint de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

def test_get_pacientes_empty(client):
    """Test obtener pacientes cuando la lista está vacía"""
    response = client.get('/pacientes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_paciente(client, sample_paciente):
    """Test crear un nuevo paciente"""
    response = client.post('/pacientes', json=sample_paciente)
    assert response.status_code == 201
    data = response.get_json()
    assert data['nombre'] == sample_paciente['nombre']
    assert data['cedula'] == sample_paciente['cedula']
    assert 'id' in data

def test_create_paciente_missing_fields(client):
    """Test crear paciente sin campos requeridos"""
    response = client.post('/pacientes', json={'nombre': 'Juan'})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_create_paciente_duplicate_cedula(client, sample_paciente):
    """Test crear paciente con cédula duplicada"""
    client.post('/pacientes', json=sample_paciente)
    response = client.post('/pacientes', json=sample_paciente)
    assert response.status_code == 400
    data = response.get_json()
    assert 'cédula' in data['error'].lower()

def test_get_paciente_by_id(client, sample_paciente):
    """Test obtener un paciente por ID"""
    # Crear paciente
    create_response = client.post('/pacientes', json=sample_paciente)
    paciente_id = create_response.get_json()['id']
    
    # Obtener paciente
    response = client.get(f'/pacientes/{paciente_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == paciente_id
    assert data['nombre'] == sample_paciente['nombre']

def test_get_paciente_not_found(client):
    """Test obtener un paciente que no existe"""
    response = client.get('/pacientes/999')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_update_paciente(client, sample_paciente):
    """Test actualizar un paciente"""
    # Crear paciente
    create_response = client.post('/pacientes', json=sample_paciente)
    paciente_id = create_response.get_json()['id']
    
    # Actualizar paciente
    update_data = {'telefono': '3009999999', 'email': 'nuevo@email.com'}
    response = client.put(f'/pacientes/{paciente_id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['telefono'] == update_data['telefono']
    assert data['email'] == update_data['email']

def test_update_paciente_not_found(client):
    """Test actualizar un paciente que no existe"""
    response = client.put('/pacientes/999', json={'telefono': '3001234567'})
    assert response.status_code == 404

def test_delete_paciente(client, sample_paciente):
    """Test eliminar un paciente"""
    # Crear paciente
    create_response = client.post('/pacientes', json=sample_paciente)
    paciente_id = create_response.get_json()['id']
    
    # Eliminar paciente
    response = client.delete(f'/pacientes/{paciente_id}')
    assert response.status_code == 200
    
    # Verificar que no existe
    get_response = client.get(f'/pacientes/{paciente_id}')
    assert get_response.status_code == 404

def test_delete_paciente_not_found(client):
    """Test eliminar un paciente que no existe"""
    response = client.delete('/pacientes/999')
    assert response.status_code == 404

def test_get_all_pacientes(client, sample_paciente):
    """Test obtener todos los pacientes"""
    # Crear varios pacientes
    client.post('/pacientes', json=sample_paciente)
    
    sample_paciente2 = sample_paciente.copy()
    sample_paciente2['cedula'] = '0987654321'
    sample_paciente2['nombre'] = 'María'
    client.post('/pacientes', json=sample_paciente2)
    
    # Obtener todos
    response = client.get('/pacientes')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
