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

# Modelo de Cita
class Cita(db.Model):
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    medico = db.Column(db.String(100), nullable=False)
    motivo = db.Column(db.Text)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'especialidad': self.especialidad,
            'medico': self.medico,
            'motivo': self.motivo,
            'estado': self.estado,
            'observaciones': self.observaciones,
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
    return jsonify({'status': 'Citas service is running'}), 200

@app.route('/citas', methods=['GET'])
def get_citas():
    """Obtener todas las citas"""
    try:
        citas = Cita.query.all()
        return jsonify([cita.to_dict() for cita in citas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/citas/<int:id>', methods=['GET'])
def get_cita(id):
    """Obtener una cita por ID"""
    try:
        cita = Cita.query.get(id)
        if not cita:
            return jsonify({'error': 'Cita no encontrada'}), 404
        return jsonify(cita.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/citas/paciente/<int:paciente_id>', methods=['GET'])
def get_citas_by_paciente(paciente_id):
    """Obtener todas las citas de un paciente"""
    try:
        citas = Cita.query.filter_by(paciente_id=paciente_id).all()
        return jsonify([cita.to_dict() for cita in citas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/citas', methods=['POST'])
def create_cita():
    """Crear una nueva cita"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['paciente_id', 'fecha_hora', 'especialidad', 'medico']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} es requerido'}), 400
        
        # Convertir fecha y hora
        fecha_hora = datetime.strptime(data['fecha_hora'], '%Y-%m-%d %H:%M:%S')
        
        # Validar que la fecha sea futura
        if fecha_hora < datetime.utcnow():
            return jsonify({'error': 'La fecha de la cita debe ser futura'}), 400
        
        # Verificar disponibilidad (mismo médico, misma hora)
        existing = Cita.query.filter_by(
            medico=data['medico'],
            fecha_hora=fecha_hora,
            estado='confirmada'
        ).first()
        if existing:
            return jsonify({'error': 'Ya existe una cita confirmada para ese médico en ese horario'}), 400
        
        # Crear cita
        cita = Cita(
            paciente_id=data['paciente_id'],
            fecha_hora=fecha_hora,
            especialidad=data['especialidad'],
            medico=data['medico'],
            motivo=data.get('motivo'),
            estado=data.get('estado', 'pendiente'),
            observaciones=data.get('observaciones')
        )
        
        db.session.add(cita)
        db.session.commit()
        
        return jsonify(cita.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/citas/<int:id>', methods=['PUT'])
def update_cita(id):
    """Actualizar una cita"""
    try:
        cita = Cita.query.get(id)
        if not cita:
            return jsonify({'error': 'Cita no encontrada'}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'paciente_id' in data:
            cita.paciente_id = data['paciente_id']
        if 'fecha_hora' in data:
            fecha_hora = datetime.strptime(data['fecha_hora'], '%Y-%m-%d %H:%M:%S')
            if fecha_hora < datetime.utcnow():
                return jsonify({'error': 'La fecha de la cita debe ser futura'}), 400
            cita.fecha_hora = fecha_hora
        if 'especialidad' in data:
            cita.especialidad = data['especialidad']
        if 'medico' in data:
            cita.medico = data['medico']
        if 'motivo' in data:
            cita.motivo = data['motivo']
        if 'estado' in data:
            if data['estado'] not in ['pendiente', 'confirmada', 'cancelada', 'completada']:
                return jsonify({'error': 'Estado inválido'}), 400
            cita.estado = data['estado']
        if 'observaciones' in data:
            cita.observaciones = data['observaciones']
        
        cita.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(cita.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/citas/<int:id>', methods=['DELETE'])
def delete_cita(id):
    """Eliminar una cita"""
    try:
        cita = Cita.query.get(id)
        if not cita:
            return jsonify({'error': 'Cita no encontrada'}), 404
        
        db.session.delete(cita)
        db.session.commit()
        
        return jsonify({'message': 'Cita eliminada correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
