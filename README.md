# API REST de Citas Médicas - Arquitectura de Microservicios

Sistema de gestión de citas médicas desarrollado con arquitectura de microservicios usando Flask, PostgreSQL y Docker.

## 🏗️ Arquitectura

El proyecto está compuesto por:

- **API Gateway** (Puerto 5000): Punto de entrada único que enruta las peticiones a los microservicios
- **Microservicio de Pacientes** (Puerto 5001): Gestión completa de pacientes (CRUD)
- **Microservicio de Citas** (Puerto 5002): Gestión completa de citas médicas (CRUD)
- **PostgreSQL** (Puerto 5432): Base de datos centralizada con tablas separadas

```
┌─────────────────┐
│   API Gateway   │ :5000
│  (Punto único)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Pacient│ │ Citas │
│Service│ │Service│
│ :5001 │ │ :5002 │
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │PostgreSQL│
    │  :5432  │
    └─────────┘
```

## 📋 Prerequisitos

- Docker Desktop instalado
- Python 3.11+ (para desarrollo local)
- Postman (para testing de la API)
- Git

## 🚀 Instalación y Ejecución

### Opción 1: Con Docker (Recomendado)

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd citas_medicas
```

2. **Construir y levantar todos los servicios**
```bash
docker-compose up --build
```

3. **Verificar que los servicios estén corriendo**
```bash
docker-compose ps
```

Deberías ver 4 contenedores corriendo:
- `api_gateway` (puerto 5000)
- `pacientes_service` (puerto 5001)
- `citas_service` (puerto 5002)
- `citas_postgres` (puerto 5432)

4. **Probar la API**
```bash
curl http://localhost:5000/health
```

### Opción 2: Desarrollo Local

1. **Iniciar PostgreSQL con Docker**
```bash
docker run --name postgres_citas -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=citas_medicas -p 5432:5432 -d postgres:15-alpine
```

2. **Instalar dependencias y ejecutar cada servicio**

**API Gateway:**
```bash
cd api-gateway
pip install -r requirements.txt
python app.py
```

**Servicio de Pacientes:**
```bash
cd pacientes-service
pip install -r requirements.txt
python app.py
```

**Servicio de Citas:**
```bash
cd citas-service
pip install -r requirements.txt
python app.py
```

## 🧪 Pruebas

### Pruebas Unitarias

**Microservicio de Pacientes:**
```bash
cd pacientes-service
pip install -r requirements.txt -r requirements-test.txt
pytest test_app.py -v
```

**Microservicio de Citas:**
```bash
cd citas-service
pip install -r requirements.txt -r requirements-test.txt
pytest test_app.py -v
```

**Con cobertura:**
```bash
pytest test_app.py -v --cov=app --cov-report=html
```

### Pruebas con Postman

1. Importar la colección `Citas_Medicas_API.postman_collection.json` en Postman
2. La colección incluye:
   - Health checks
   - CRUD de Pacientes
   - CRUD de Citas
   - Pruebas de validación
   - Casos de error

## 📚 Documentación de la API

### Endpoints - API Gateway

**Base URL:** `http://localhost:5000`

#### Pacientes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/pacientes` | Obtener todos los pacientes |
| GET | `/api/pacientes/{id}` | Obtener un paciente por ID |
| POST | `/api/pacientes` | Crear un nuevo paciente |
| PUT | `/api/pacientes/{id}` | Actualizar un paciente |
| DELETE | `/api/pacientes/{id}` | Eliminar un paciente |

**Ejemplo de creación de paciente:**
```json
{
    "nombre": "Juan",
    "apellido": "Pérez",
    "cedula": "1234567890",
    "fecha_nacimiento": "1990-05-15",
    "telefono": "3001234567",
    "email": "juan.perez@email.com",
    "direccion": "Calle 123 #45-67"
}
```

#### Citas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/citas` | Obtener todas las citas |
| GET | `/api/citas/{id}` | Obtener una cita por ID |
| GET | `/api/citas/paciente/{id}` | Obtener citas de un paciente |
| POST | `/api/citas` | Crear una nueva cita |
| PUT | `/api/citas/{id}` | Actualizar una cita |
| DELETE | `/api/citas/{id}` | Eliminar una cita |

**Ejemplo de creación de cita:**
```json
{
    "paciente_id": 1,
    "fecha_hora": "2025-12-20 15:00:00",
    "especialidad": "Cardiología",
    "medico": "Dr. López",
    "motivo": "Consulta de control",
    "estado": "pendiente",
    "observaciones": "Traer exámenes previos"
}
```

**Estados de cita:**
- `pendiente`: Cita programada pero no confirmada
- `confirmada`: Cita confirmada por el paciente
- `cancelada`: Cita cancelada
- `completada`: Cita realizada

## 🐳 Comandos Docker Útiles

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api-gateway

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reconstruir servicios
docker-compose up --build

# Ver estado de los servicios
docker-compose ps
```

## 🌐 Despliegue en Render

### 1. Preparar el repositorio

Asegúrate de que tu código esté en un repositorio de Git (GitHub, GitLab, etc.).

### 2. Desplegar PostgreSQL

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en "New +" → "PostgreSQL"
3. Configura:
   - **Name:** citas-medicas-db
   - **Database:** citas_medicas
   - **User:** postgres
   - **Region:** Selecciona la más cercana
4. Click en "Create Database"
5. **Guarda la URL interna** (Internal Database URL)

### 3. Desplegar Microservicios

#### Servicio de Pacientes

1. Click en "New +" → "Web Service"
2. Conecta tu repositorio
3. Configura:
   - **Name:** pacientes-service
   - **Root Directory:** `pacientes-service`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
4. Variables de entorno:
   - `DATABASE_URL`: [URL interna de PostgreSQL]
   - `PORT`: 5001
5. Click en "Create Web Service"

#### Servicio de Citas

1. Click en "New +" → "Web Service"
2. Conecta tu repositorio
3. Configura:
   - **Name:** citas-service
   - **Root Directory:** `citas-service`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
4. Variables de entorno:
   - `DATABASE_URL`: [URL interna de PostgreSQL]
   - `PORT`: 5002
5. Click en "Create Web Service"

#### API Gateway

1. Click en "New +" → "Web Service"
2. Conecta tu repositorio
3. Configura:
   - **Name:** api-gateway
   - **Root Directory:** `api-gateway`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
4. Variables de entorno:
   - `PACIENTES_SERVICE_URL`: https://pacientes-service.onrender.com
   - `CITAS_SERVICE_URL`: https://citas-service.onrender.com
   - `PORT`: 5000
5. Click en "Create Web Service"

### 4. Inicializar la Base de Datos

Una vez desplegados los servicios, ejecuta el script SQL de inicialización:

1. Ve al dashboard de PostgreSQL en Render
2. Click en "Connect" → "External Connection"
3. Usa un cliente PostgreSQL (pgAdmin, DBeaver, etc.) para conectarte
4. Ejecuta el contenido de `database/init.sql`

### 5. Probar el despliegue

Usa Postman para probar tu API en producción:
- URL Base: `https://api-gateway.onrender.com`
- Ejemplo: `https://api-gateway.onrender.com/health`

## 📁 Estructura del Proyecto

```
citas_medicas/
├── api-gateway/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── pacientes-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── requirements-test.txt
│   ├── test_app.py
│   └── Dockerfile
├── citas-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── requirements-test.txt
│   ├── test_app.py
│   └── Dockerfile
├── database/
│   └── init.sql
├── docker-compose.yml
├── .gitignore
├── .dockerignore
├── Citas_Medicas_API.postman_collection.json
└── README.md
```

## 🔧 Tecnologías Utilizadas

- **Backend:** Flask 3.0.0
- **ORM:** SQLAlchemy 3.1.1
- **Base de Datos:** PostgreSQL 15
- **Testing:** Pytest 7.4.3
- **Contenedores:** Docker & Docker Compose
- **WSGI Server:** Gunicorn 21.2.0

## 🛠️ Características Principales

- ✅ Arquitectura de microservicios
- ✅ API Gateway como punto de entrada único
- ✅ Base de datos PostgreSQL centralizada
- ✅ Contenedorización completa con Docker
- ✅ Pruebas unitarias con pytest
- ✅ Validaciones de datos
- ✅ Manejo de errores
- ✅ Health checks
- ✅ Colección de Postman completa
- ✅ Listo para despliegue en la nube

## 📝 Notas Importantes

1. **Datos de ejemplo:** La base de datos se inicializa con datos de ejemplo (ver `database/init.sql`)
2. **Validaciones:** 
   - La cédula debe ser única
   - Las fechas de citas deben ser futuras
   - No se permiten citas duplicadas (mismo médico, misma hora)
3. **Estados de cita:** `pendiente`, `confirmada`, `cancelada`, `completada`
4. **Formato de fechas:**
   - Fecha de nacimiento: `YYYY-MM-DD`
   - Fecha y hora de cita: `YYYY-MM-DD HH:MM:SS`

## 🐛 Troubleshooting

### Error: "Connection refused" al conectar a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Reiniciar servicios
docker-compose restart
```

### Error: "Port already in use"
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :5000

# Matar el proceso o cambiar el puerto en docker-compose.yml
```

### Los servicios no se comunican
```bash
# Verificar que estén en la misma red
docker network inspect citas_medicas_citas_network

# Verificar logs
docker-compose logs -f
```

## 📞 Soporte

Para reportar problemas o sugerencias, crea un issue en el repositorio.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**Desarrollado con ❤️ para gestión de citas médicas**
