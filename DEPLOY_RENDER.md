# 🚀 Guía de Despliegue en Render - Plan Free

Esta guía te permitirá desplegar el proyecto en Render con **una sola base de datos PostgreSQL** (limitación del plan free).

## 📋 Requisitos Previos

- Cuenta en [Render](https://render.com) (plan free)
- Repositorio en GitHub: https://github.com/valentinaBarreto18/citas_medicas
- Cuenta de GitHub vinculada a Render

---

## 🗄️ PASO 1: Crear la Base de Datos PostgreSQL

Esta será la **única base de datos** que usaremos para ambos microservicios.

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en **"New +"** → **"PostgreSQL"**
3. Configura:
   - **Name:** `citas-medicas-db`
   - **Database:** `citas_medicas`
   - **User:** `postgres` (por defecto)
   - **Region:** Selecciona la más cercana (Oregon USA o Frankfurt)
   - **PostgreSQL Version:** 15 (recomendado)
   - **Plan:** Free

4. Click en **"Create Database"**
5. Espera 1-2 minutos a que se cree

### 📝 Guardar URLs de Conexión

Una vez creada, en la página de la base de datos encontrarás:

- **Internal Database URL** (para los servicios en Render)
- **External Database URL** (para conectarte desde fuera)

**Copia y guarda la Internal Database URL**, se ve así:
```
postgresql://postgres:XXXXXXXXXXXX@dpg-XXXXXXX/citas_medicas
```

---

## 🔧 PASO 2: Inicializar la Base de Datos

Necesitas ejecutar el script SQL de inicialización. Tienes 2 opciones:

### **Opción A: Desde Render Dashboard (Recomendada)**

1. En la página de tu base de datos en Render
2. Ve a la pestaña **"Shell"** o **"Connect"**
3. Click en **"PSQL Command"**
4. Se abrirá una terminal web conectada a tu base de datos
5. Copia y pega el contenido del archivo `database/init.sql`
6. Presiona Enter para ejecutarlo

### **Opción B: Desde tu PC con pgAdmin o psql**

1. Instala [pgAdmin](https://www.pgadmin.org/download/) o usa psql
2. Conéctate usando la **External Database URL**
3. Ejecuta el script `database/init.sql`

---

## 🚀 PASO 3: Desplegar Microservicio de Pacientes

1. En Render Dashboard, click en **"New +"** → **"Web Service"**

2. Conecta tu repositorio de GitHub:
   - Click en **"Connect a repository"**
   - Autoriza a Render si es la primera vez
   - Selecciona: `valentinaBarreto18/citas_medicas`

3. Configura el servicio:
   ```
   Name:                 pacientes-service
   Region:               Oregon (USA) o la misma que la BD
   Branch:               master
   Root Directory:       pacientes-service
   Runtime:              Python 3
   Build Command:        pip install -r requirements.txt
   Start Command:        gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
   ```

4. En **"Advanced"**, agrega las variables de entorno:
   - Click en **"Add Environment Variable"**
   - Variable 1:
     - **Key:** `DATABASE_URL`
     - **Value:** [Pega aquí la Internal Database URL que guardaste en el Paso 1]
   - Variable 2:
     - **Key:** `PORT`
     - **Value:** `5001`

5. Plan: Selecciona **"Free"**

6. Click en **"Create Web Service"**

7. Espera 5-10 minutos a que se despliegue

8. **IMPORTANTE: Guarda la URL del servicio**, se verá así:
   ```
   https://pacientes-service-XXXX.onrender.com
   ```

---

## 🚀 PASO 4: Desplegar Microservicio de Citas

1. En Render Dashboard, click en **"New +"** → **"Web Service"**

2. Conecta el mismo repositorio: `valentinaBarreto18/citas_medicas`

3. Configura el servicio:
   ```
   Name:                 citas-service
   Region:               Oregon (USA) o la misma que la BD
   Branch:               master
   Root Directory:       citas-service
   Runtime:              Python 3
   Build Command:        pip install -r requirements.txt
   Start Command:        gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
   ```

4. En **"Advanced"**, agrega las variables de entorno:
   - Variable 1:
     - **Key:** `DATABASE_URL`
     - **Value:** [Pega la misma Internal Database URL del Paso 1]
   - Variable 2:
     - **Key:** `PORT`
     - **Value:** `5002`

5. Plan: **"Free"**

6. Click en **"Create Web Service"**

7. Espera 5-10 minutos a que se despliegue

8. **Guarda la URL del servicio:**
   ```
   https://citas-service-XXXX.onrender.com
   ```

---

## 🌐 PASO 5: Desplegar API Gateway

1. En Render Dashboard, click en **"New +"** → **"Web Service"**

2. Conecta el repositorio: `valentinaBarreto18/citas_medicas`

3. Configura el servicio:
   ```
   Name:                 api-gateway
   Region:               Oregon (USA)
   Branch:               master
   Root Directory:       api-gateway
   Runtime:              Python 3
   Build Command:        pip install -r requirements.txt
   Start Command:        gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
   ```

4. En **"Advanced"**, agrega las variables de entorno:
   - Variable 1:
     - **Key:** `PACIENTES_SERVICE_URL`
     - **Value:** `https://pacientes-service-XXXX.onrender.com` (URL del Paso 3)
   - Variable 2:
     - **Key:** `CITAS_SERVICE_URL`
     - **Value:** `https://citas-service-XXXX.onrender.com` (URL del Paso 4)
   - Variable 3:
     - **Key:** `PORT`
     - **Value:** `5000`

5. Plan: **"Free"**

6. Click en **"Create Web Service"**

7. Espera 5-10 minutos

8. **Esta será tu URL pública de la API:**
   ```
   https://api-gateway-XXXX.onrender.com
   ```

---

## ✅ PASO 6: Verificar el Despliegue

Una vez que todos los servicios muestren el estado **"Live"** en verde:

### 1. Prueba el Health Check

Abre en tu navegador:
```
https://api-gateway-XXXX.onrender.com/health
```

Deberías ver:
```json
{"status":"API Gateway is running"}
```

### 2. Prueba listar pacientes

```
https://api-gateway-XXXX.onrender.com/api/pacientes
```

Deberías ver los 3 pacientes de ejemplo del script SQL.

### 3. Prueba listar citas

```
https://api-gateway-XXXX.onrender.com/api/citas
```

---

## 🔄 PASO 7: Configurar Postman para Producción

1. Abre Postman
2. Importa la colección: `Citas_Medicas_API.postman_collection.json`
3. En Variables (abajo de la colección):
   - Cambia `base_url` de `http://localhost:5000` a:
   - `https://api-gateway-XXXX.onrender.com` (tu URL del API Gateway)
4. Guarda los cambios
5. Ahora puedes ejecutar todas las pruebas contra producción

---

## ⚠️ LIMITACIONES DEL PLAN FREE

### 1. **Servicios se duermen después de 15 minutos de inactividad**
   - Primera petición después de dormir: **tardará 50-60 segundos**
   - Solución: Hacer una petición "calentamiento" antes de usar

### 2. **Solo una base de datos PostgreSQL**
   - ✅ Resuelto: Ambos microservicios usan la misma BD con tablas separadas

### 3. **750 horas/mes por servicio**
   - Con 4 servicios (BD + 3 web services) es suficiente para desarrollo/demo

### 4. **Reinicios automáticos**
   - Los servicios free se reinician periódicamente
   - No es problema para este tipo de aplicación

---

## 🐛 TROUBLESHOOTING

### Error: "Application failed to respond"
- **Causa:** El servicio está arrancando (primera vez)
- **Solución:** Espera 1-2 minutos más

### Error: "Build failed"
- **Causa:** Error en requirements.txt o en el código
- **Solución:** Revisa los logs en Render Dashboard → Tu servicio → Logs

### Error de conexión a base de datos
- **Causa:** URL de base de datos incorrecta
- **Solución:** 
  1. Ve a tu base de datos en Render
  2. Copia la "Internal Database URL" completa
  3. Actualiza la variable `DATABASE_URL` en cada servicio
  4. Redespliega (Manual Deploy)

### Los microservicios no se comunican
- **Causa:** URLs incorrectas en el API Gateway
- **Solución:**
  1. Ve a cada microservicio y copia su URL completa
  2. Actualiza `PACIENTES_SERVICE_URL` y `CITAS_SERVICE_URL` en el Gateway
  3. Redespliega el Gateway

### "Relation 'pacientes' does not exist"
- **Causa:** No ejecutaste el script SQL de inicialización
- **Solución:** Ve al Paso 2 y ejecuta `database/init.sql`

---

## 📊 MONITOREO

### Ver logs en tiempo real:
1. Ve a Render Dashboard
2. Selecciona el servicio
3. Pestaña **"Logs"**
4. Los logs se actualizan en tiempo real

### Verificar salud de los servicios:
```
https://api-gateway-XXXX.onrender.com/health
https://pacientes-service-XXXX.onrender.com/health
https://citas-service-XXXX.onrender.com/health
```

---

## 🔄 ACTUALIZAR EL CÓDIGO

Cuando hagas cambios en tu código:

1. **Commit y push a GitHub:**
   ```bash
   git add .
   git commit -m "Descripción del cambio"
   git push origin master
   ```

2. **Render redesplega automáticamente** (en 2-3 minutos)

3. **O manualmente:**
   - Ve al servicio en Render Dashboard
   - Click en **"Manual Deploy"** → **"Deploy latest commit"**

---

## 📝 RESUMEN DE URLs

Al final tendrás estas URLs (guárdalas):

```
Base de Datos:
- Internal: postgresql://postgres:XXXX@dpg-XXXX/citas_medicas

Servicios:
- API Gateway:     https://api-gateway-XXXX.onrender.com
- Pacientes:       https://pacientes-service-XXXX.onrender.com
- Citas:           https://citas-service-XXXX.onrender.com
```

---

## 🎉 ¡LISTO!

Tu API de Citas Médicas está desplegada en producción con:
- ✅ 3 microservicios independientes
- ✅ 1 base de datos PostgreSQL compartida
- ✅ API Gateway funcionando
- ✅ Completamente gratis en Render

**URL pública de tu API:**
```
https://api-gateway-XXXX.onrender.com
```

Puedes compartir esta URL para que otros prueben tu API o usarla en un frontend.

---

## 📚 RECURSOS ADICIONALES

- [Documentación de Render](https://render.com/docs)
- [Guía de PostgreSQL en Render](https://render.com/docs/databases)
- [Troubleshooting de Python en Render](https://render.com/docs/deploy-flask)

---

**¿Problemas? Revisa la sección de Troubleshooting o los logs en Render Dashboard.**
