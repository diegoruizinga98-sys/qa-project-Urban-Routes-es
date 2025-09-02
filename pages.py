# pages.py
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)

from helpers import retrieve_phone_code


class UrbanRoutesPage:
    # -----------------
    # Localizadores UI
    # -----------------
    from_field = (By.ID, "from")
    to_field = (By.ID, "to")
    initial_order_btn = (By.CSS_SELECTOR, "button.button.round")

    # Tarifa Comfort (tarjeta) y estado "seleccionado" robusto
    comfort_tariff_card = (By.XPATH, "//div[div[normalize-space(text())='Comfort']]")
    comfort_tariff_card_active = (
        By.XPATH,
        # Caso A: el estado activo está en el mismo contenedor de la tarjeta
        "//div[div[normalize-space(text())='Comfort']]["
        "  contains(@class,'active') or contains(@class,'selected') or "
        "  @aria-selected='true' or @aria-pressed='true' or "
        "  .//input[@type='radio' and (@checked='true' or @checked)]"
        "]"
        " | "
        # Caso B: el estado activo vive en un ancestro del título "Comfort"
        "//div[normalize-space(text())='Comfort']/ancestor::*["
        "  contains(@class,'active') or contains(@class,'selected') or "
        "  @aria-selected='true' or @aria-pressed='true' or "
        "  .//input[@type='radio' and (@checked='true' or @checked)]"
        "][1]"
    )

    # Teléfono (modal)
    phone_placeholder = (By.XPATH, "//div[normalize-space(text())='Número de teléfono']")
    phone_modal_field = (By.ID, "phone")
    phone_modal_next_btn = (By.XPATH, "//div[@class='modal']//button[normalize-space(text())='Siguiente']")
    sms_modal_field = (By.ID, "code")
    sms_modal_confirm_btn = (By.XPATH, "//div[@class='modal']//button[normalize-space(text())='Confirmar']")

    # Pago (tarjeta)
    payment_method_placeholder = (By.CSS_SELECTOR, ".pp-button.filled")
    add_card_option = (By.CSS_SELECTOR, ".pp-plus")
    card_number_field = (By.ID, "number")
    card_cvv_field = (By.CSS_SELECTOR, ".card-code-input #code")
    card_add_button = (By.XPATH, "//button[normalize-space(text())='Agregar' and not(@disabled)]")
    payment_close_buttons = (By.CSS_SELECTOR, "button.close-button.section-close")

    # Mensaje al conductor
    driver_message_field = (By.ID, "comment")

    # Requisitos (manta/pañuelos, helados, etc.)
    requirements_section = (By.CSS_SELECTOR, "div.reqs")
    requirements_chevron = (
        By.XPATH,
        "//div[contains(@class,'reqs-header')]//*[contains(@class,'reqs-arrow') or (@alt='Arrow')]"
    )
    blanket_and_tissues_switch = (
        By.XPATH,
        "//div[contains(@class,'r-sw-container')]"
        "[div[@class='r-sw-label' and normalize-space(text())='Manta y pañuelos']]"
        "//input[@type='checkbox']"
    )

    # Contador de Helado (valor y botón +)
    ice_cream_plus = (
        By.XPATH,
        "//div[@class='r-counter-label' and normalize-space(text())='Helado']"
        "/ancestor::div[contains(@class,'r-counter-container')]"
        "//div[contains(@class,'counter-plus')]"
    )
    ice_cream_value = (
        By.XPATH,
        "//div[div[normalize-space(text())='Helado']]"
        "//div[contains(@class,'counter-value')]"
    )

    # Botón final de pedir taxi
    final_order_button = (By.CSS_SELECTOR, ".smart-button")

    # Modal de buscar/asignar automóvil
    driver_search_modal_title = (By.XPATH, "//*[contains(normalize-space(.),'Buscar automóvil')]")
    driver_info_modal_title = (
        By.XPATH,
        "//*[contains(normalize-space(.),'estará aquí') or contains(normalize-space(.),'min estará')]"
    )

    # ---------------
    # Constructor
    # ---------------
    def __init__(self, driver, timeout=40):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # -----------------------
    # Helpers base (robustez)
    # -----------------------
    def _tick(self, ms=200):
        """Pequeña espera cooperativa para permitir re-render/animaciones."""
        self.driver.execute_async_script(
            """
            const cb = arguments[arguments.length-1];
            setTimeout(cb, arguments[0]);
            """,
            ms,
        )

    def _wait_enabled(self, locator, timeout=20):
        """Espera a que el elemento esté visible, con tamaño >0 y no disabled/aria-disabled."""
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

    def _safe_click(self, locator, retries=3, pause=0.2):
        """Click robusto: intenta normal y, si hay overlay/intercept, usa click JS; reintenta en staleness."""
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
        return False

    def _type(self, locator, text):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(text)
        return el

    def _scroll_to(self, locator):
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        return el

    def _click_first_visible(self, locator) -> bool:
        """Para listas de botones/cerrar; hace click al primero visible/habilitado."""
        self.wait.until(EC.presence_of_all_elements_located(locator))
        for el in self.driver.find_elements(*locator):
            try:
                if el.is_displayed() and el.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                    sleep(0.1)
                    self.driver.execute_script("arguments[0].click();", el)
                    return True
            except Exception:
                continue
        return False

    # ------------------------
    # Steps (alto nivel / POM)
    # ------------------------
    def set_route(self, from_addr: str, to_addr: str):
        """Escribe origen/destino y deja listo el botón de ir a pedido."""
        from_el = self._type(self.from_field, from_addr)
        sleep(1.2)
        from_el.send_keys(Keys.ENTER)

        to_el = self._type(self.to_field, to_addr)
        sleep(1.2)
        to_el.send_keys(Keys.ENTER)

        self.wait.until(EC.text_to_be_present_in_element_value(self.to_field, to_addr))
        self.wait.until(EC.element_to_be_clickable(self.initial_order_btn))

    def go_to_order_screen(self):
        """Abre la pantalla donde aparecen las tarifas (Comfort, etc.)."""
        self._safe_click(self.initial_order_btn)
        self.wait.until(EC.visibility_of_element_located(self.comfort_tariff_card))

    def set_address(self, from_addr: str, to_addr: str):
        """Alias que usan tus tests: configura dirección y abre la pantalla de pedido."""
        self.set_route(from_addr, to_addr)
        self.go_to_order_screen()

    def select_comfort_tariff(self):
        """Selecciona la tarjeta Comfort y espera a que quede en estado 'seleccionado'."""
        self._safe_click(self.comfort_tariff_card)
        self._tick(150)
        self.wait.until(EC.presence_of_element_located(self.comfort_tariff_card_active))

    def fill_phone_number(self, phone: str):
        """Completa teléfono y confirma SMS usando CDP (requiere Network.enable en el fixture)."""
        self._safe_click(self.phone_placeholder)
        self._type(self.phone_modal_field, phone)
        self._safe_click(self.phone_modal_next_btn)
        code = retrieve_phone_code(self.driver)
        self._type(self.sms_modal_field, code)
        self._safe_click(self.sms_modal_confirm_btn)
        self.wait.until(EC.invisibility_of_element_located(self.sms_modal_field))

    def add_credit_card(self, number: str, cvv: str):
        """Agrega tarjeta como método de pago, evitando overlays que interceptan el click."""
        try:
            overlay = (By.CSS_SELECTOR, ".overlay, .modal-overlay, .loading-overlay")
            self.wait.until(EC.invisibility_of_element_located(overlay))
        except Exception:
            pass

        self._safe_click(self.payment_method_placeholder)
        self.wait.until(EC.visibility_of_element_located(self.add_card_option))
        self._safe_click(self.add_card_option)

        self.wait.until(EC.visibility_of_element_located(self.card_number_field))
        self._type(self.card_number_field, number)
        cvv_el = self._type(self.card_cvv_field, cvv)
        cvv_el.send_keys(Keys.TAB)

        self.wait.until(EC.element_to_be_clickable(self.card_add_button))
        self._safe_click(self.card_add_button)

        # Cierra el panel si hay botón de cerrar visible
        self._click_first_visible(self.payment_close_buttons)

    def set_driver_message(self, message: str):
        """Escribe un mensaje para el conductor."""
        self.wait.until(EC.visibility_of_element_located(self.driver_message_field)).clear()
        self.wait.until(EC.visibility_of_element_located(self.driver_message_field)).send_keys(message)

    def _open_requirements_if_needed(self):
        """Abre la sección de requisitos si está colapsada."""
        reqs_element = self.wait.until(EC.presence_of_element_located(self.requirements_section))
        chevron = reqs_element.find_element(*self.requirements_chevron)
        is_open = "open" in (reqs_element.get_attribute("class") or "")
        if not is_open:
            self.driver.execute_script("arguments[0].click();", chevron)
            self.wait.until(lambda d: "open" in (reqs_element.get_attribute("class") or ""))

    def add_blanket_and_tissues(self):
        """Activa el switch 'Manta y pañuelos'."""
        self._open_requirements_if_needed()
        container = self.driver.find_element(
            By.XPATH,
            "//div[contains(@class,'r-sw-container')]"
            "[div[@class='r-sw-label' and normalize-space(text())='Manta y pañuelos']]"
        )
        checkbox = container.find_element(By.CSS_SELECTOR, ".switch-input")
        slider = container.find_element(By.CSS_SELECTOR, ".slider.round")
        if not checkbox.is_selected():
            self.driver.execute_script("arguments[0].click();", slider)
            sleep(0.2)

    def add_two_ice_creams(self):
        """Incrementa el contador de 'Helado' a +2."""
        self._open_requirements_if_needed()
        plus = self.wait.until(EC.presence_of_element_located(self.ice_cream_plus))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", plus)
        self.driver.execute_script("arguments[0].click();", plus)
        sleep(0.12)
        self.driver.execute_script("arguments[0].click();", plus)

    def order_taxi(self):
        """Pulsa 'Pedir taxi' y espera el modal de búsqueda."""
        btn = self._wait_enabled(self.final_order_button)
        self._tick(180)
        self._safe_click(self.final_order_button)
        self._tick(300)
        try:
            self.wait.until(EC.visibility_of_element_located(self.driver_search_modal_title))
        except Exception:
            # En algunas variantes aparece rápido y desaparece: damos una gracia
            self._tick(600)
