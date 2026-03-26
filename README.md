# 🚗 Urban Routes — Selenium WebDriver Automation

**QA Automation Engineer:** Diego Ruiz Inga  
**Sprint:** 9 · TripleTen QA Bootcamp  
**Stack:** Python 3.11 · Selenium WebDriver · Pytest · Page Object Model · CDP Logs · Edge WebDriver

---

## 📋 Descripción del proyecto

Automatización E2E del flujo completo de pedido de taxi en la plataforma web **Urban Routes**, aplicando el patrón **Page Object Model (POM)** en 3 capas (pages, helpers, data).

El flujo cubre 8 pasos críticos: selección de ruta, tarifa Comfort, número de teléfono, código SMS vía CDP, tarjeta de crédito, mensaje al conductor, manta y pañuelos, pedido final.

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
| Tasa de aprobación en sprint | **67%** (67/100 casos funcionales) |

---

## 🚀 Cómo ejecutar

1. Clonar el repositorio: git clone https://github.com/diegoruizinga98-sys/qa-project-Urban-Routes-es.git
2. Instalar dependencias: pip install -r requirements.txt
3. Verificar que Edge WebDriver está en la ruta configurada en main.py
4. Ejecutar las pruebas: pytest test_main.py -v

---

## 👤 Autor

**Diego Ruiz Inga** · QA Automation Engineer  
🌐 [Portafolio](https://diegoruizinga98-sys.github.io/diego-ruiz-inga-qa/) · [LinkedIn](https://www.linkedin.com/in/diego-ruiz-inga/) · 📧 diegori466@gmail.com
