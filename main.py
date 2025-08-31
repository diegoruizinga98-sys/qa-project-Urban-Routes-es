# main.py
import data
from time import sleep
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

DRIVER_PATH = r"C:\Users\MASTER98\projects\qa-project-Urban-Routes-es\msedgedriver.exe"


# ------------------------------
# Utilitario: normalizar la URL
# ------------------------------
def normalize_url(u: str) -> str:
    u = (u or "").strip().strip('"').strip("'")
    if not u:
        raise ValueError("La URL de Urban Routes está vacía.")
    parsed = urlparse(u)
    if not parsed.scheme:
        u = "https://" + u
    return u


# ----------------------------------------
# Captura el código de confirmación (CDP)
# ----------------------------------------
def retrieve_phone_code(driver) -> str:
    import json
    import time as _t
    from selenium.common import WebDriverException
    code = None
    for _ in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance')
                    if log.get("message") and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd(
                    'Network.getResponseBody', {'requestId': message_data["params"]["requestId"]}
                )
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            _t.sleep(1)
            continue
        if code:
            return code
    raise Exception("No se encontró el código de confirmación del teléfono.")


# =========================
# PAGE OBJECT MODEL (POM)
# =========================
class UrbanRoutesPage:
    # -----------------
    # Localizadores UI
    # -----------------
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    initial_order_btn = (By.CSS_SELECTOR, "button.button.round")
    comfort_tariff_card = (By.XPATH, "//div[div[text()='Comfort']]")

    phone_placeholder = (By.XPATH, "//div[text()='Número de teléfono']")
    phone_modal_field = (By.ID, "phone")
    phone_modal_next_btn = (By.XPATH, "//div[@class='modal']//button[text()='Siguiente']")
    sms_modal_field = (By.ID, "code")
    sms_modal_confirm_btn = (By.XPATH, "//div[@class='modal']//button[text()='Confirmar']")

    payment_method_placeholder = (By.CSS_SELECTOR, ".pp-button.filled")
    add_card_option = (By.CSS_SELECTOR, ".pp-plus")
    card_number_field = (By.ID, "number")
    card_cvv_field = (By.CSS_SELECTOR, ".card-code-input #code")
    card_add_button = (By.XPATH, "//button[text()='Agregar' and not(@disabled)]")
    payment_close_buttons = (By.CSS_SELECTOR, "button.close-button.section-close")

    driver_message = (By.ID, "comment")

    # Requisitos del pedido / chevron / switches / counters
    reqs_section = (By.CSS_SELECTOR, "div.reqs")
    reqs_header_chevron = (
        By.XPATH,
        "//div[contains(@class,'reqs-header')]//*[contains(@class,'reqs-arrow') or (@alt='Arrow')]"
    )

    # Botón final de pedir taxi
    final_order_btn = (By.CSS_SELECTOR, ".smart-button")

    # Textos del modal de búsqueda / asignación (espera hasta 31 s)
    searching_title = (By.XPATH, "//*[contains(normalize-space(.),'Buscar automóvil')]")
    assigned_title_hint = (By.XPATH, "//*[contains(normalize-space(.),'estará aquí') or contains(normalize-space(.),'min estará')]")

    # ---------------
    # Constructor
    # ---------------
    def __init__(self, driver, timeout=40):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self._last_from = None
        self._last_to = None

    # -----------------------
    # Helpers de estabilidad
    # -----------------------
    def _tick(self, ms=250):
        """Pequeña espera cooperativa para que React termine microtareas/animaciones."""
        self.driver.execute_async_script("""
            const cb = arguments[arguments.length-1];
            setTimeout(cb, arguments[0]);
        """, ms)

    def _wait_enabled(self, locator, timeout=20):
        """Espera a que un elemento esté visible, con tamaño y no disabled/aria-disabled."""
        el = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

        def _enabled(_):
            try:
                if not el.is_displayed():
                    return False
                if el.rect.get("width", 0) == 0 or el.rect.get("height", 0) == 0:
                    return False
                dis = el.get_attribute("disabled")
                aria = (el.get_attribute("aria-disabled") or "").lower()
                return (dis is None) and (aria in ("", "false"))
            except StaleElementReferenceException:
                return False

        WebDriverWait(self.driver, timeout).until(_enabled, "Elemento no habilitado/estable a tiempo")
        return el

    def _safe_click(self, locator, retries=3, pause=0.25):
        """Click robusto con reintentos y fallback JS si hay overlays/animaciones."""
        for _ in range(retries):
            try:
                el = self._wait_enabled(locator)
                try:
                    el.click()
                except (ElementClickInterceptedException, ElementNotInteractableException):
                    self.driver.execute_script("arguments[0].click();", el)
                return True
            except StaleElementReferenceException:
                sleep(pause)
                continue
        return False

    # ------------------
    # Acciones atómicas
    # ------------------
    def _force_click(self, locator):
        """Click por JS (útil para atravesar overlays)."""
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        sleep(0.3)
        self.driver.execute_script("arguments[0].click();", element)

    def _type(self, locator, text):
        """Escribir texto en un input visible."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        return element

    def _scroll_to(self, locator):
        """Scroll al elemento objetivo (centra en viewport)."""
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        return el

    def _click_first_visible(self, locator) -> bool:
        """Click al primer elemento visible/habilitado de un grupo (p.ej. varios botones de cerrar)."""
        self.wait.until(EC.presence_of_all_elements_located(locator))
        for el in self.driver.find_elements(*locator):
            try:
                if el.is_displayed() and el.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    sleep(0.2)
                    self.driver.execute_script("arguments[0].click();", el)
                    return True
            except Exception:
                continue
        return False

    def _close_payment_section(self):
        """Cierra el panel/modal de método de pago si está presente."""
        closed = self._click_first_visible(self.payment_close_buttons)
        if not closed:
            for el in self.driver.find_elements(*self.payment_close_buttons):
                try:
                    self.driver.execute_script("arguments[0].click();", el)
                    break
                except Exception:
                    continue
        sleep(0.3)

    # --------------------
    # Helpers de Requisitos
    # --------------------
    def _toggle_switch_by_label(self, label_text: str, desired_on: bool = True):
        """Activa/desactiva un switch identificado por su etiqueta visible."""
        sw_container = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//div[contains(@class,'r-sw-container')]"
            f"[div[@class='r-sw-label' and normalize-space(text())='{label_text}']]"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sw_container)
        checkbox = sw_container.find_element(By.CSS_SELECTOR, ".switch-input")
        slider = sw_container.find_element(By.CSS_SELECTOR, ".slider.round")
        if checkbox.is_selected() != desired_on:
            self.driver.execute_script("arguments[0].click();", slider)
            sleep(0.2)

    def _increase_counter_by_label(self, label_text: str, times: int = 1):
        """Pulsa el botón '+' de un contador identificado por su etiqueta visible."""
        plus = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//div[@class='r-counter-label' and normalize-space(text())='{label_text}']"
            f"/ancestor::div[contains(@class,'r-counter-container')]"
            f"//div[contains(@class,'counter-plus')]"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", plus)
        for _ in range(times):
            self.driver.execute_script("arguments[0].click();", plus)
            sleep(0.15)

    # ------------------------
    # Pasos (alto nivel / POM)
    # ------------------------
    def set_route(self, from_addr: str, to_addr: str):
        # #1 Escribir origen y confirmar
        self._last_from, self._last_to = from_addr, to_addr
        from_element = self._type(self.from_field, from_addr)
        sleep(1.5)
        from_element.send_keys(Keys.ENTER)

        # #2 Escribir destino y confirmar
        to_element = self._type(self.to_field, to_addr)
        sleep(1.5)
        to_element.send_keys(Keys.ENTER)

        # #3 Verificar que el destino quedó seteado y que el botón inicial está habilitado
        self.wait.until(EC.text_to_be_present_in_element_value(self.to_field, to_addr))
        self.wait.until(EC.element_to_be_clickable(self.initial_order_btn))

    def go_to_order_screen(self):
        # #4 Ir a la pantalla de pedido
        self._safe_click(self.initial_order_btn)
        self.wait.until(EC.visibility_of_element_located(self.comfort_tariff_card))

    def select_comfort(self):
        # #5 Seleccionar tarifa "Comfort"
        self._safe_click(self.comfort_tariff_card)

    def fill_phone(self, phone: str):
        # #6 Completar teléfono y confirmar SMS
        self._safe_click(self.phone_placeholder)
        self._type(self.phone_modal_field, phone)
        self._safe_click(self.phone_modal_next_btn)
        code = retrieve_phone_code(self.driver)
        self._type(self.sms_modal_field, code)
        self._safe_click(self.sms_modal_confirm_btn)
        self.wait.until(EC.invisibility_of_element_located(self.sms_modal_field))

    def add_card(self, number: str, cvv: str):
        # #7 Agregar tarjeta como método de pago y cerrar panel
        self._safe_click(self.payment_method_placeholder)
        self.wait.until(EC.visibility_of_element_located(self.add_card_option))
        self._safe_click(self.add_card_option)
        self.wait.until(EC.visibility_of_element_located(self.card_number_field))
        self._type(self.card_number_field, number)
        cvv_el = self._type(self.card_cvv_field, cvv)
        cvv_el.send_keys(Keys.TAB)
        self.wait.until(EC.element_to_be_clickable(self.card_add_button))
        self._safe_click(self.card_add_button)
        self._close_payment_section()

    def set_message(self, msg: str):
        # #8 Escribir mensaje para el conductor
        self._type(self.driver_message, msg)

    def add_extras(self, ice_creams_to_add=2):
        # #9 Abrir "Requisitos del pedido", activar switches y sumar helados
        section = self._scroll_to(self.reqs_section)
        chevron = section.find_element(*self.reqs_header_chevron)
        is_open = "open" in section.get_attribute("class")
        if not is_open:
            self.driver.execute_script("arguments[0].click();", chevron)
            self.wait.until(lambda d: "open" in section.get_attribute("class"))
        else:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", chevron)

        # Activa switches deseados
        self._toggle_switch_by_label("Manta y pañuelos", desired_on=True)
        self._toggle_switch_by_label("Cortina acústica", desired_on=True)

        # Sumar helados
        self._increase_counter_by_label("Helado", times=ice_creams_to_add)

    def order_final_taxi(self):
        # #10 Clic robusto en "Pedir taxi" (con reintento si no cambia el estado)
        btn = self._wait_enabled(self.final_order_btn)
        self._tick(200)
        self._safe_click(self.final_order_btn)
        self._tick(350)

        def _state_changed():
            try:
                disabled = btn.get_attribute("disabled") is not None
                aria_dis = (btn.get_attribute("aria-disabled") or "").lower() == "true"
                cls = (btn.get_attribute("class") or "").lower()
                return disabled or aria_dis or ("loading" in cls or "processing" in cls)
            except StaleElementReferenceException:
                return True  # el DOM cambió: consideramos que avanzó

        if not _state_changed():
            # Hacer un segundo intento automático si no hubo cambio
            self._tick(500)
            self._safe_click(self.final_order_btn)
            self._tick(400)

        # #11 Esperar el modal de "Buscar automóvil" y su transición (hasta 31 s)
        try:
            search_el = WebDriverWait(self.driver, 6).until(
                EC.visibility_of_element_located(self.searching_title)
            )
        except Exception:
            search_el = None

        if search_el:
            def advanced(_):
                try:
                    if not search_el.is_displayed():
                        return True
                    text_now = (search_el.text or "").strip()
                    if "Buscar automóvil" not in text_now:
                        return True
                except StaleElementReferenceException:
                    return True
                try:
                    self.driver.find_element(*self.assigned_title_hint)
                    return True
                except Exception:
                    return False

            WebDriverWait(self.driver, 31).until(advanced, "No avanzó el estado del modal en 31s")
        else:
            self._tick(1200)


# =========================
# TESTS (pytest style)
# =========================
class TestUrbanRoutes:
    driver = None
    page = None

    @classmethod
    def setup_class(cls):
        # #A Inicializa Edge con logs de red para capturar el código SMS
        options = EdgeOptions()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
        service = EdgeService(executable_path=DRIVER_PATH)
        cls.driver = webdriver.Edge(service=service, options=options)
        cls.driver.maximize_window()
        cls.page = UrbanRoutesPage(cls.driver)

    def test_set_route(self):
        # #B Abre la app y fija origen/destino
        self.driver.get(normalize_url(data.urban_routes_url))
        p = self.page
        p.set_route(data.address_from, data.address_to)
        assert data.address_from in self.driver.find_element(*p.from_field).get_attribute('value')
        assert data.address_to in self.driver.find_element(*p.to_field).get_attribute('value')

    def test_full_order_flow(self):
        # #C Flujo completo hasta pedir taxi y esperar asignación
        self.driver.get(normalize_url(data.urban_routes_url))
        p = self.page

        p.set_route(data.address_from, data.address_to)      # Ruta
        p.go_to_order_screen()                               # Pedido
        p.select_comfort()                                   # Tarifa
        p.fill_phone(data.phone_number)                      # Teléfono + SMS
        p.add_card(data.card_number, data.card_code)         # Tarjeta

        sleep(1)  # estabilización ligera

        p.set_message(data.message_for_driver)               # Mensaje
        p.add_extras(ice_creams_to_add=2)                    # Requisitos
        p.order_final_taxi()                                 # Pedir taxi + espera

        assert True

    @classmethod
    def teardown_class(cls):
        # #D Cierre de navegador
        sleep(15)
        cls.driver.quit()
