from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/citas_medicas'
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Paciente
class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'cedula': self.cedula,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Crear tablas (solo si no estamos en modo testing)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'Pacientes service is running'}), 200

@app.route('/pacientes', methods=['GET'])
def get_pacientes():
    """Obtener todos los pacientes"""
    try:
        pacientes = Paciente.query.all()
        return jsonify([paciente.to_dict() for paciente in pacientes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pacientes/<int:id>', methods=['GET'])
def get_paciente(id):
    """Obtener un paciente por ID"""
    try:
        paciente = Paciente.query.get(id)
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        return jsonify(paciente.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pacientes', methods=['POST'])
def create_paciente():
    """Crear un nuevo paciente"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Verificar si ya existe un paciente con esa cédula
        existing = Paciente.query.filter_by(cedula=data['cedula']).first()
        if existing:
            return jsonify({'error': 'Ya existe un paciente con esa cédula'}), 400
        
        # Convertir fecha de nacimiento
        fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        
        # Crear paciente
        paciente = Paciente(
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            fecha_nacimiento=fecha_nacimiento,
            telefono=data.get('telefono'),
            email=data.get('email'),
            direccion=data.get('direccion')
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        return jsonify(paciente.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/pacientes/<int:id>', methods=['PUT'])
def update_paciente(id):
    """Actualizar un paciente"""
    try:
        paciente = Paciente.query.get(id)
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'nombre' in data:
            paciente.nombre = data['nombre']
        if 'apellido' in data:
            paciente.apellido = data['apellido']
        if 'cedula' in data:
            # Verificar que no exista otra cédula igual
            existing = Paciente.query.filter_by(cedula=data['cedula']).first()
            if existing and existing.id != id:
                return jsonify({'error': 'Ya existe un paciente con esa cédula'}), 400
            paciente.cedula = data['cedula']
        if 'fecha_nacimiento' in data:
            paciente.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        if 'telefono' in data:
            paciente.telefono = data['telefono']
        if 'email' in data:
            paciente.email = data['email']
        if 'direccion' in data:
            paciente.direccion = data['direccion']
        
        paciente.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(paciente.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/pacientes/<int:id>', methods=['DELETE'])
def delete_paciente(id):
    """Eliminar un paciente"""
    try:
        paciente = Paciente.query.get(id)
        if not paciente:
            return jsonify({'error': 'Paciente no encontrado'}), 404
        
        db.session.delete(paciente)
        db.session.commit()
        
        return jsonify({'message': 'Paciente eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
