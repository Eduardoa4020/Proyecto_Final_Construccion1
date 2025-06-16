# Sistema de Monitoreo de Atención en el Aula

## Integrantes

- Eduardo Elias Alvarado Escobar  
- Alexis David Cajamarca Largo  
- Gabriel Andres Asuncion Perez  

## Instrucciones de instalación y ejecución

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   cd tu-repositorio
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Realiza las migraciones de la base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Ejecuta el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

6. **Accede a la aplicación:**
   Abre tu navegador y entra a [http://localhost:8000/](http://localhost:8000/)

## Breve descripción de funcionalidades

- **Monitoreo en tiempo real:** Permite analizar la atención de los estudiantes en el aula usando la cámara web.
- **Detección de atención, distracción y somnolencia:** El sistema procesa imágenes y muestra estadísticas en tiempo real.
- **Registro de eventos:** Guarda un historial de eventos detectados durante la sesión.
- **Panel de control:** Interfaz amigable para iniciar/detener el monitoreo y visualizar resultados.
- **Gestión de usuarios y autenticación:** Acceso seguro para profesores y administradores.

## Recursos estáticos

- Las imágenes y archivos estáticos (como el favicon) están ubicados en la carpeta `static/` y correctamente referenciados en los archivos HTML usando la etiqueta `{% static %}` de Django.
- Ejemplo de referencia en el código:
  ```html
  <link rel="icon" type="image/x-icon" href="{% static 'Authentication/favicon.ico' %}">
  ```
