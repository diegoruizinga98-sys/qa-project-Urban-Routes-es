# Urban Routes Prueba Web Selenium Sprint 8 QA - 35
# Diego Ruiz Inga

## Descripción del Proyecto
Este proyecto implementa la automatización de pruebas para la aplicación **Urban Routes**, que simula el flujo completo de un pedido de taxi en una plataforma web.  
Incluye desde la selección de ruta, la confirmación de teléfono, el agregado de un método de pago, hasta el pedido final de un taxi y la validación de la asignación del conductor.

## Tecnologías y Técnicas Utilizadas
- **Python 3.11**
- **Selenium WebDriver** (automatización de UI)
- **Pytest** (framework de pruebas)
- **Edge WebDriver** (para ejecutar las pruebas en Microsoft Edge)
- **Page Object Model (POM)** (patrón de diseño aplicado a las pruebas)
- **CDP Logs (Chrome DevTools Protocol)** para recuperar el código de confirmación por SMS

## Estructura del Proyecto
- main.py # Archivo principal con POM y pruebas
- data.py # Datos de prueba (rutas, números, tarjetas, mensajes)
- README.md # Documentación del proyecto

## Funcionalidad
## ▶️ Ejecución de las Pruebas
1. Clonar el repositorio.
2. Instalar dependencias:
   pip install -r requirements.txt
3. Verificar que el Edge WebDriver está en la ruta configurada en main.py. 
4. Ejecutar las pruebas con PyCharm:
    pytest main.py -v

## Resumen
Flujo Automatizado
1. Abrir la aplicación Urban Routes. 
2. Ingresar dirección de origen y destino. 
3. Seleccionar la tarifa Comfort. 
4. Confirmar número telefónico con código SMS. 
5. Agregar método de pago (tarjeta). 
6. Escribir mensaje para el conductor. 
7. Abrir la sección de requisitos, activar switches y añadir helados. 
8. Pedir taxi y esperar hasta la asignación de un conductor.