import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import data
from pages import UrbanRoutesPage
from helpers import normalize_url

@pytest.fixture(scope="class", name="browser")
def browser():
    options = EdgeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    d = webdriver.Edge(options=options)
    d.execute_cdp_cmd("Network.enable", {})
    yield d
    d.quit()


@pytest.fixture(scope="class")
def page(browser):
    return UrbanRoutesPage(browser)

@pytest.mark.usefixtures("browser", "page")
class TestUrbanRoutes:
    """
    Clase que agrupa las 9 pruebas del flujo de Urban Routes.
    """

    # Usa 'page' y su 'page.driver', no el viejo 'driver' para evitar None
    def test_1_set_address(self, page):
        page.driver.get(normalize_url(data.urban_routes_url))
        page.set_address(data.address_from, data.address_to)
        assert page.wait.until(EC.visibility_of_element_located(page.comfort_tariff_card)), \
            "Fallo en Prueba 1: La tarifa Comfort no apareció."

    def test_2_select_comfort_tariff(self, page):
        page.select_comfort_tariff()
        assert page.driver.find_element(*page.comfort_tariff_card_active), \
            "Fallo en Prueba 2: La tarifa Comfort no fue seleccionada."

    def test_3_fill_phone_number(self, page):
        page.fill_phone_number(data.phone_number)
        assert page.wait.until(EC.visibility_of_element_located(page.payment_method_placeholder)), \
            "Fallo en Prueba 3: El campo de método de pago no apareció."

    def test_4_add_credit_card(self, page):
        page.add_credit_card(data.card_number, data.card_code)
        assert page.wait.until(EC.visibility_of_element_located(page.final_order_button)), \
            "Fallo en Prueba 4: El botón para pedir taxi no está visible."

    def test_5_set_driver_message(self, page):
        page.set_driver_message(data.message_for_driver)
        message_field = page.driver.find_element(*page.driver_message_field)
        assert message_field.get_attribute('value') == data.message_for_driver, \
            "Fallo en Prueba 5: El mensaje para el conductor no se escribió."

    def test_6_add_blanket_and_tissues(self, page):
        page.add_blanket_and_tissues()
        checkbox = page.driver.find_element(*page.blanket_and_tissues_switch)
        assert checkbox.is_selected(), "Fallo en Prueba 6: 'Manta y pañuelos' no fue seleccionado."

    def test_7_add_two_ice_creams(self, page):
        page.add_two_ice_creams()
        counter_locator = (By.XPATH, "//div[div[text()='Helado']]//div[contains(@class, 'counter-value')]")
        counter_value = page.wait.until(EC.visibility_of_element_located(counter_locator))
        assert counter_value.text.strip() in {"2", "02"}, "Fallo en Prueba 7: No se agregaron 2 helados."

    def test_8_order_taxi(self, page):
        page.order_taxi()
        assert page.wait.until(EC.visibility_of_element_located(page.driver_search_modal_title)), \
            "Fallo en Prueba 8: El modal 'Buscar automóvil' no apareció."

    def test_9_wait_for_driver_info(self, page):
        long_wait = WebDriverWait(page.driver, 60)
        assert long_wait.until(EC.visibility_of_element_located(page.driver_info_modal_title)), \
            "Fallo en Prueba 9: La info del conductor no apareció en 60 segundos."