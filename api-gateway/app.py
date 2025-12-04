from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# URLs de los microservicios
PACIENTES_SERVICE_URL = os.getenv('PACIENTES_SERVICE_URL', 'http://localhost:5001')
CITAS_SERVICE_URL = os.getenv('CITAS_SERVICE_URL', 'http://localhost:5002')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'API Gateway is running'}), 200

# ==================== RUTAS PARA PACIENTES ====================

@app.route('/api/pacientes', methods=['GET'])
def get_pacientes():
    """Obtener todos los pacientes"""
    try:
        response = requests.get(f'{PACIENTES_SERVICE_URL}/pacientes')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Pacientes service unavailable', 'details': str(e)}), 503

@app.route('/api/pacientes/<int:id>', methods=['GET'])
def get_paciente(id):
    """Obtener un paciente por ID"""
    try:
        response = requests.get(f'{PACIENTES_SERVICE_URL}/pacientes/{id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Pacientes service unavailable', 'details': str(e)}), 503

@app.route('/api/pacientes', methods=['POST'])
def create_paciente():
    """Crear un nuevo paciente"""
    try:
        response = requests.post(
            f'{PACIENTES_SERVICE_URL}/pacientes',
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Pacientes service unavailable', 'details': str(e)}), 503

@app.route('/api/pacientes/<int:id>', methods=['PUT'])
def update_paciente(id):
    """Actualizar un paciente"""
    try:
        response = requests.put(
            f'{PACIENTES_SERVICE_URL}/pacientes/{id}',
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Pacientes service unavailable', 'details': str(e)}), 503

@app.route('/api/pacientes/<int:id>', methods=['DELETE'])
def delete_paciente(id):
    """Eliminar un paciente"""
    try:
        response = requests.delete(f'{PACIENTES_SERVICE_URL}/pacientes/{id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Pacientes service unavailable', 'details': str(e)}), 503

# ==================== RUTAS PARA CITAS ====================

@app.route('/api/citas', methods=['GET'])
def get_citas():
    """Obtener todas las citas"""
    try:
        response = requests.get(f'{CITAS_SERVICE_URL}/citas')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

@app.route('/api/citas/<int:id>', methods=['GET'])
def get_cita(id):
    """Obtener una cita por ID"""
    try:
        response = requests.get(f'{CITAS_SERVICE_URL}/citas/{id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

@app.route('/api/citas/paciente/<int:paciente_id>', methods=['GET'])
def get_citas_by_paciente(paciente_id):
    """Obtener todas las citas de un paciente"""
    try:
        response = requests.get(f'{CITAS_SERVICE_URL}/citas/paciente/{paciente_id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

@app.route('/api/citas', methods=['POST'])
def create_cita():
    """Crear una nueva cita"""
    try:
        response = requests.post(
            f'{CITAS_SERVICE_URL}/citas',
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

@app.route('/api/citas/<int:id>', methods=['PUT'])
def update_cita(id):
    """Actualizar una cita"""
    try:
        response = requests.put(
            f'{CITAS_SERVICE_URL}/citas/{id}',
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

@app.route('/api/citas/<int:id>', methods=['DELETE'])
def delete_cita(id):
    """Eliminar una cita"""
    try:
        response = requests.delete(f'{CITAS_SERVICE_URL}/citas/{id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Citas service unavailable', 'details': str(e)}), 503

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
