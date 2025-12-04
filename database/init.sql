-- Script de inicialización de la base de datos
-- Se ejecuta automáticamente al crear el contenedor de PostgreSQL

-- Crear la base de datos si no existe
SELECT 'CREATE DATABASE citas_medicas'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'citas_medicas')\gexec

-- Conectar a la base de datos
\c citas_medicas;

-- Tabla de Pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(120),
    direccion VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Citas
CREATE TABLE IF NOT EXISTS citas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    especialidad VARCHAR(100) NOT NULL,
    medico VARCHAR(100) NOT NULL,
    motivo TEXT,
    estado VARCHAR(20) DEFAULT 'pendiente',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paciente FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_pacientes_cedula ON pacientes(cedula);
CREATE INDEX IF NOT EXISTS idx_citas_paciente_id ON citas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_citas_fecha_hora ON citas(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado);
CREATE INDEX IF NOT EXISTS idx_citas_medico ON citas(medico);

-- Datos de ejemplo (opcional)
INSERT INTO pacientes (nombre, apellido, cedula, fecha_nacimiento, telefono, email, direccion)
VALUES 
    ('Juan', 'Pérez', '1234567890', '1990-05-15', '3001234567', 'juan.perez@email.com', 'Calle 123 #45-67'),
    ('María', 'García', '0987654321', '1985-08-22', '3009876543', 'maria.garcia@email.com', 'Carrera 45 #67-89'),
    ('Carlos', 'Rodríguez', '1122334455', '1978-12-10', '3005551234', 'carlos.rodriguez@email.com', 'Avenida 78 #12-34')
ON CONFLICT (cedula) DO NOTHING;

-- Insertar citas de ejemplo
INSERT INTO citas (paciente_id, fecha_hora, especialidad, medico, motivo, estado, observaciones)
VALUES 
    (1, '2025-12-10 10:00:00', 'Medicina General', 'Dr. López', 'Consulta de rutina', 'confirmada', 'Traer exámenes previos'),
    (1, '2025-12-15 14:30:00', 'Cardiología', 'Dra. Martínez', 'Control cardiológico', 'pendiente', NULL),
    (2, '2025-12-12 09:00:00', 'Dermatología', 'Dr. Gómez', 'Revisión de piel', 'confirmada', NULL)
ON CONFLICT DO NOTHING;

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
DROP TRIGGER IF EXISTS update_pacientes_updated_at ON pacientes;
CREATE TRIGGER update_pacientes_updated_at
    BEFORE UPDATE ON pacientes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_citas_updated_at ON citas;
CREATE TRIGGER update_citas_updated_at
    BEFORE UPDATE ON citas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
