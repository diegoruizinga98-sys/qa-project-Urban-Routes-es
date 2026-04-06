# 🚗 Urban Routes — Selenium WebDriver Automation

Proyecto de automatización E2E para **Urban Routes**, una plataforma web de solicitud de taxis que integra múltiples métodos de pago, tarifas y asignación de conductores en tiempo real.

La suite cubre el flujo crítico de negocio de extremo a extremo: desde la selección de ruta hasta la confirmación del conductor, garantizando que cada paso funcione correctamente antes de llegar a producción.

**Stack:** Python 3.11 · Selenium WebDriver · Pytest · Page Object Model · CDP Logs · Edge WebDriver

---

## 📋 Contexto del proyecto

**Urban Routes** es una aplicación web que permite a usuarios solicitar taxis configurando origen, destino, tipo de tarifa y método de pago. El flujo de compra involucra interacciones complejas entre múltiples componentes de UI, validación de formularios y comunicación con servicios externos (verificación de teléfono vía SMS).

La automatización se diseñó para reemplazar la regresión manual que consumía ~30 minutos por ciclo, aplicando **Page Object Model en 3 capas** para maximizar el mantenimiento y la reutilización del código.

**Resultado clave:** ⬇️ **97% de reducción en tiempo de regresión** (30 min manuales → menos de 1 min automatizado)

---

## 🏗️ Arquitectura POM — 3 capas

| Archivo | Responsabilidad |
|---|---|
| pages.py | Locators + acciones por página (capa de UI) |
| helpers.py | Lógica reutilizable y utilidades (capa de negocio) |
| data.py | Datos de prueba: rutas, tarjetas, mensajes |
| test_main.py | Casos de prueba E2E con Pytest |
| requirements.txt | Dependencias del proyecto |

---

## ✅ Flujo automatizado (8 pasos)

| # | Paso | Verificación |
|---|------|-------------|
| 1 | Configurar dirección de origen y destino | Campo ruta completo |
| 2 | Seleccionar tarifa **Comfort** | Tarifa activa visible |
| 3 | Ingresar número de teléfono | Campo validado |
| 4 | Obtener código SMS vía **CDP Logs** | Código capturado automáticamente |
| 5 | Agregar tarjeta de crédito y confirmar | Tarjeta agregada |
| 6 | Escribir mensaje al conductor | Campo con texto |
| 7 | Activar manta y pañuelos | Toggle activo |
| 8 | Pedir taxi y validar asignación de conductor | Modal de confirmación visible |

---

## 💻 Tecnologías utilizadas

| Herramienta | Uso |
|---|---|
| **Selenium WebDriver** | Automatización de UI web |
| **Pytest** | Framework de pruebas y reportes |
| **Page Object Model** | Arquitectura de 3 capas (pages/helpers/data) |
| **CDP Logs** | Captura de código SMS sin acceso real |
| **Edge WebDriver** | Driver configurado para Microsoft Edge |
| **Python 3.11** | Lenguaje principal |

---

## 📊 Resultados

| Métrica | Valor |
|---|---|
| Casos de prueba automatizados | 8 steps E2E |
| Tiempo de ejecución | < 1 min |
| Tiempo manual previo | ~30 min |
| Reducción de tiempo de regresión | **97%** |
| Tasa de aprobación | **67%** (67/100 casos funcionales) |

---

## 🚀 Cómo ejecutar

1. Clonar el repositorio: git clone https://github.com/diegoruizinga98-sys/qa-project-Urban-Routes-es.git
2. Instalar dependencias: pip install -r requirements.txt
3. Verificar que Edge WebDriver está en la ruta configurada en main.py
4. Ejecutar las pruebas: pytest test_main.py -v

---

## 👤 Autor

**Diego Ruiz Inga** · QA Automation Engineer  
🌐 [Portafolio](https://diegoruizinga98-sys.github.io/diego-ruiz-inga-qa/) · [LinkedIn](https://www.linkedin.com/in/diego-ruiz-inga/) · 📧 ruizingadiego@gmail.com
