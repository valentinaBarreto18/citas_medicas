import pytest
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio del servicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Cita

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
def sample_cita():
    """Datos de ejemplo para una cita"""
    fecha_futura = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    return {
        'paciente_id': 1,
        'fecha_hora': fecha_futura,
        'especialidad': 'Medicina General',
        'medico': 'Dr. López',
        'motivo': 'Consulta de rutina',
        'estado': 'pendiente',
        'observaciones': 'Traer exámenes previos'
    }

def test_health_check(client):
    """Test del endpoint de health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

def test_get_citas_empty(client):
    """Test obtener citas cuando la lista está vacía"""
    response = client.get('/citas')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_cita(client, sample_cita):
    """Test crear una nueva cita"""
    response = client.post('/citas', json=sample_cita)
    assert response.status_code == 201
    data = response.get_json()
    assert data['paciente_id'] == sample_cita['paciente_id']
    assert data['especialidad'] == sample_cita['especialidad']
    assert 'id' in data

def test_create_cita_missing_fields(client):
    """Test crear cita sin campos requeridos"""
    response = client.post('/citas', json={'paciente_id': 1})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_create_cita_past_date(client, sample_cita):
    """Test crear cita con fecha pasada"""
    sample_cita['fecha_hora'] = '2020-01-01 10:00:00'
    response = client.post('/citas', json=sample_cita)
    assert response.status_code == 400
    data = response.get_json()
    assert 'futura' in data['error'].lower()

def test_create_cita_duplicate_slot(client, sample_cita):
    """Test crear cita en horario ya ocupado"""
    sample_cita['estado'] = 'confirmada'
    client.post('/citas', json=sample_cita)
    
    # Intentar crear otra cita en el mismo horario con el mismo médico
    response = client.post('/citas', json=sample_cita)
    assert response.status_code == 400
    data = response.get_json()
    assert 'confirmada' in data['error'].lower()

def test_get_cita_by_id(client, sample_cita):
    """Test obtener una cita por ID"""
    # Crear cita
    create_response = client.post('/citas', json=sample_cita)
    cita_id = create_response.get_json()['id']
    
    # Obtener cita
    response = client.get(f'/citas/{cita_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == cita_id
    assert data['especialidad'] == sample_cita['especialidad']

def test_get_cita_not_found(client):
    """Test obtener una cita que no existe"""
    response = client.get('/citas/999')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_get_citas_by_paciente(client, sample_cita):
    """Test obtener todas las citas de un paciente"""
    # Crear varias citas para el mismo paciente
    client.post('/citas', json=sample_cita)
    
    sample_cita2 = sample_cita.copy()
    fecha_futura2 = (datetime.utcnow() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
    sample_cita2['fecha_hora'] = fecha_futura2
    sample_cita2['especialidad'] = 'Cardiología'
    client.post('/citas', json=sample_cita2)
    
    # Obtener todas las citas del paciente
    response = client.get(f'/citas/paciente/{sample_cita["paciente_id"]}')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

def test_update_cita(client, sample_cita):
    """Test actualizar una cita"""
    # Crear cita
    create_response = client.post('/citas', json=sample_cita)
    cita_id = create_response.get_json()['id']
    
    # Actualizar cita
    update_data = {'estado': 'confirmada', 'observaciones': 'Cita confirmada'}
    response = client.put(f'/citas/{cita_id}', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['estado'] == update_data['estado']
    assert data['observaciones'] == update_data['observaciones']

def test_update_cita_invalid_estado(client, sample_cita):
    """Test actualizar cita con estado inválido"""
    create_response = client.post('/citas', json=sample_cita)
    cita_id = create_response.get_json()['id']
    
    response = client.put(f'/citas/{cita_id}', json={'estado': 'invalido'})
    assert response.status_code == 400

def test_update_cita_not_found(client):
    """Test actualizar una cita que no existe"""
    response = client.put('/citas/999', json={'estado': 'confirmada'})
    assert response.status_code == 404

def test_delete_cita(client, sample_cita):
    """Test eliminar una cita"""
    # Crear cita
    create_response = client.post('/citas', json=sample_cita)
    cita_id = create_response.get_json()['id']
    
    # Eliminar cita
    response = client.delete(f'/citas/{cita_id}')
    assert response.status_code == 200
    
    # Verificar que no existe
    get_response = client.get(f'/citas/{cita_id}')
    assert get_response.status_code == 404

def test_delete_cita_not_found(client):
    """Test eliminar una cita que no existe"""
    response = client.delete('/citas/999')
    assert response.status_code == 404

def test_get_all_citas(client, sample_cita):
    """Test obtener todas las citas"""
    # Crear varias citas
    client.post('/citas', json=sample_cita)
    
    sample_cita2 = sample_cita.copy()
    sample_cita2['paciente_id'] = 2
    fecha_futura2 = (datetime.utcnow() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
    sample_cita2['fecha_hora'] = fecha_futura2
    client.post('/citas', json=sample_cita2)
    
    # Obtener todas
    response = client.get('/citas')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
