import json
import time as _t
from selenium.common import WebDriverException


def retrieve_phone_code(driver) -> str:
    """
    Lee Performance Logs y usa CDP para extraer el código.
    Requiere: logging performance + Network.enable ya activados.
    """
    import json, time as _t
    from selenium.common import WebDriverException

    vistos = set()
    for _ in range(20):  # ~20 s
        try:
            for entry in reversed(driver.get_log("performance")):
                raw = entry.get("message")
                if not raw:
                    continue
                try:
                    m = json.loads(raw).get("message", {})
                except json.JSONDecodeError:
                    continue

                if m.get("method") != "Network.responseReceived":
                    continue

                p = m.get("params", {})
                resp = p.get("response", {})
                url = resp.get("url", "")
                req_id = p.get("requestId")

                if "api/v1/number?number=" in url and req_id and req_id not in vistos:
                    vistos.add(req_id)
                    try:
                        body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})
                        digits = "".join(ch for ch in body.get("body", "") if ch.isdigit())
                        if digits:
                            return digits
                    except WebDriverException:
                        pass
        except WebDriverException:
            pass
        _t.sleep(1)
    raise Exception("No se encontró el código de confirmación del teléfono.")




def normalize_url(u: str) -> str:
    """Normaliza la URL para asegurar que tenga el esquema https."""
    from urllib.parse import urlparse
    u = (u or "").strip().strip('"').strip("'")
    if not u:
        raise ValueError("La URL de Urban Routes está vacía.")
    parsed = urlparse(u)
    if not parsed.scheme:
        u = "https://" + u
    return u

