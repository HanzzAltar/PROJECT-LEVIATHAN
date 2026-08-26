
from __future__ import annotations

import getpass
import hashlib
import itertools
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote, urlparse

import requests


# ============================================================
# 01. APP CONFIGURATION
# ============================================================

APP_NAME = "PROJECT-LEVIATHAN"
APP_VERSION = "1.0"
DEBUG = False

REQUEST_TIMEOUT = 20
DOWNLOAD_TIMEOUT = 180
MAX_RETRIES = 2

# -------------------- Alight Motion -------------------------
V1_API_URL = "https://restapidhan.vercel.app/api/am"
V1_API_KEY = "dravndesamuel"

V2_API_URL = "https://dapjimotionpro.my.id/api/proxy-amprem"
V2_ORIGIN = "https://dapjimotionpro.my.id"
V2_REFERER = "https://dapjimotionpro.my.id/generator-v2"

# -------------------- Strom AI ------------------------------
AI_CHAT_API_URL = "https://strom-ai.my.id/api/chat"
AI_CHAT_MODE = "strom"
AI_CHAT_DEFAULT_USER_ID = "termux_user"
AI_CHAT_ORIGIN = "https://strom-ai.my.id"
AI_CHAT_REFERER = "https://strom-ai.my.id/"

# -------------------- View Page Source -----------------------
VPS_TOKEN_URL = "https://www.view-page-source.com/api/token"
VPS_FETCH_URL = "https://www.view-page-source.com/api/fetch"
VPS_ORIGIN = "https://www.view-page-source.com"
VPS_REFERER = "https://www.view-page-source.com/"

# -------------------- TikTok ---------------------------------
TIKTOK_API_URL = "https://api.siputzx.my.id/api/d/tiktok/v2"
TIKTOK_REFERER = "https://api.siputzx.my.id/"

# -------------------- Web -> ZIP -----------------------------
ASPOSE_WEB_CONVERTER_URL = (
    "https://api.products.aspose.app/cells/converter/api/"
    "ConverterApi/WebConverter?outputType=ZIP"
)
ASPOSE_WEB_DOWNLOAD_URL = (
    "https://api.products.aspose.app/cells/converter/api/Download"
)
ASPOSE_ORIGIN = "https://products.aspose.app"
ASPOSE_REFERER = "https://products.aspose.app/"

# -------------------- Web -> APK -----------------------------
WEB2APK_START_URL = "https://bintangapi.my.id/api/web2apk/start.php"
WEB2APK_STATUS_URL = "https://bintangapi.my.id/api/web2apk/status.php"
WEB2APK_POLL_INTERVAL = 3
WEB2APK_MAX_POLLS = 100

WEB2APK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "*/*",
    "Origin": "https://bintangtools.web.id",
    "Referer": "https://bintangtools.web.id/",
    "Accept-Language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7",
}


# ============================================================
# 02. TERMINAL UI
# ============================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class UI:
    """Semua fungsi tampilan terminal dipusatkan di sini."""

    WIDTH_MIN = 60
    WIDTH_MAX = 96

    @staticmethod
    def width(default: int = 76) -> int:
        try:
            width = shutil.get_terminal_size((default, 24)).columns
        except OSError:
            width = default
        return max(UI.WIDTH_MIN, min(width, UI.WIDTH_MAX))

    @staticmethod
    def clear() -> None:
        print("\033[2J\033[H", end="")

    @staticmethod
    def line(char: str = "─") -> None:
        print(f"{C.GRAY}{char * (UI.width() - 2)}{C.RESET}")

    @staticmethod
    def header(title: str = APP_NAME, subtitle: str = "Modular Terminal Toolkit") -> None:
        width = UI.width()
        print(f"{C.MAGENTA}{C.BOLD}")
        print("╭" + "─" * (width - 2) + "╮")
        print("│" + title.center(width - 2) + "│")
        print("│" + subtitle.center(width - 2) + "│")
        print("╰" + "─" * (width - 2) + "╯")
        print(C.RESET)

    @staticmethod
    def section(title: str, icon: str = "◆") -> None:
        print()
        print(f"{C.CYAN}{C.BOLD}{icon} {title}{C.RESET}")
        UI.line()

    @staticmethod
    def success(text: str) -> None:
        print(f"{C.GREEN}{C.BOLD}✓ {text}{C.RESET}")

    @staticmethod
    def error(text: str) -> None:
        print(f"{C.RED}{C.BOLD}✗ {text}{C.RESET}")

    @staticmethod
    def warning(text: str) -> None:
        print(f"{C.YELLOW}{C.BOLD}! {text}{C.RESET}")

    @staticmethod
    def info(text: str) -> None:
        print(f"{C.DIM}{text}{C.RESET}")

    @staticmethod
    def label(key: str, value: str, key_width: int = 14) -> None:
        print(f"  {C.CYAN}{key:<{key_width}}{C.RESET} {value}")

    @staticmethod
    def menu_item(number: str, title: str, description: str = "") -> None:
        print(
            f"  {C.CYAN}{C.BOLD}{number:>2}{C.RESET}  "
            f"{C.WHITE}{C.BOLD}{title:<20}{C.RESET}"
            f"{C.DIM}{description}{C.RESET}"
        )

    @staticmethod
    def success_box(title: str = "SUCCESS", message: str = "") -> None:
        width = min(UI.width() - 4, 66)
        print(f"{C.GREEN}╭─ {title} " + "─" * max(1, width - len(title) - 5) + f"╮{C.RESET}")
        print(f"{C.GREEN}│{C.RESET} {message}")
        print(f"{C.GREEN}╰" + "─" * width + f"╯{C.RESET}")

    @staticmethod
    def pause(message: str = "Enter untuk kembali...") -> None:
        try:
            input(f"\n{C.CYAN}{message}{C.RESET}")
        except (EOFError, KeyboardInterrupt):
            pass


class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str) -> None:
        self.message = message
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _spin(self) -> None:
        for frame in itertools.cycle(self.FRAMES):
            if self._stop.is_set():
                break
            sys.stdout.write(
                f"\r{C.CYAN}{frame}{C.RESET} {self.message:<60}"
            )
            sys.stdout.flush()
            time.sleep(0.08)

    def __enter__(self) -> "Spinner":
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * 76 + "\r")
        sys.stdout.flush()


def startup() -> None:
    UI.clear()
    for message in ("Initializing", "Loading modules", "Preparing workspace"):
        for dots in (".", "..", "..."):
            sys.stdout.write(f"\r{C.CYAN}⠋{C.RESET} {message}{dots:<3}")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()
    UI.header()


# ============================================================
# 03. DATA MODELS & VALIDATION
# ============================================================

@dataclass(frozen=True)
class MagicMethod:
    name: str
    label: str
    endpoint: str
    http_method: str


V1 = MagicMethod("v1", "Method V1 — GET", V1_API_URL, "GET")
V2 = MagicMethod("v2", "Method V2 — POST", V2_API_URL, "POST")


class ApiError(RuntimeError):
    """Error terstandar untuk kegagalan API/network."""


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PACKAGE_RE = re.compile(
    r"[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+"
)


def validate_email(value: str) -> bool:
    return bool(EMAIL_RE.fullmatch(value))


def valid_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def valid_package_name(value: str) -> bool:
    return bool(PACKAGE_RE.fullmatch(value))


def valid_tiktok_url(value: str) -> bool:
    lower = value.lower()
    return valid_url(value) and (
        "tiktok.com/" in lower or "vt.tiktok.com/" in lower
    )


def extract_message(payload: Any, default: str = "Tidak ada pesan.") -> str:
    if isinstance(payload, dict):
        for key in ("message", "msg", "error", "detail", "content"):
            value = payload.get(key)
            if value:
                return str(value)
    if isinstance(payload, str) and payload.strip():
        return payload.strip()
    return default


def is_success(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False

    value = payload.get("status")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {
            "true", "ok", "success", "successful", "1"
        }

    return bool(payload.get("success") is True or payload.get("verified") is True)


def extract_code_order(payload: Any) -> Optional[str]:
    if not isinstance(payload, dict):
        return None
    for key in (
        "codeorder",
        "code_order",
        "codeOrder",
        "order_code",
        "orderCode",
        "code",
    ):
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def nested_dicts(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    containers = [payload]
    for key in ("data", "result"):
        value = payload.get(key)
        if isinstance(value, dict):
            containers.append(value)
    return containers


def extract_build_id(payload: Any) -> Optional[str]:
    for obj in nested_dicts(payload):
        for key in ("build_id", "buildId", "id"):
            value = obj.get(key)
            if value not in (None, ""):
                return str(value)
    return None


def extract_download_url(payload: Any) -> Optional[str]:
    for obj in nested_dicts(payload):
        for key in ("download_url", "downloadUrl", "url"):
            value = obj.get(key)
            if isinstance(value, str) and valid_url(value):
                return value
    return None


def extract_status(payload: Any) -> str:
    for obj in nested_dicts(payload):
        for key in ("status", "state"):
            value = obj.get(key)
            if value not in (None, ""):
                return str(value).strip().lower()
    return ""


def prompt_required(
    label: str,
    validator: Optional[Callable[[str], bool]] = None,
    error_message: str = "Input tidak valid.",
) -> str:
    while True:
        try:
            value = input(f"{C.CYAN}{label:<18} › {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt

        if not value:
            UI.error("Input tidak boleh kosong.")
            continue
        if validator and not validator(value):
            UI.error(error_message)
            continue
        return value


# ============================================================
# 04. HTTP CLIENT
# ============================================================

class HttpClient:
    """Lapisan HTTP generik agar retry, timeout, dan debug konsisten."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ToolsB/2.0",
            "Accept": "application/json, text/plain, */*",
        })

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: int = REQUEST_TIMEOUT,
    ) -> Any:
        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                    timeout=timeout,
                )

                try:
                    payload = response.json()
                except ValueError:
                    payload = response.text

                if response.status_code >= 400:
                    raise ApiError(
                        f"HTTP {response.status_code}: "
                        f"{extract_message(payload)}"
                    )

                if DEBUG:
                    self._debug_payload(payload)

                return payload

            except (requests.RequestException, ApiError) as exc:
                last_error = exc
                if attempt <= MAX_RETRIES:
                    time.sleep(0.7 * attempt)

        raise ApiError(str(last_error) if last_error else "Request gagal.")

    @staticmethod
    def _debug_payload(payload: Any) -> None:
        if isinstance(payload, dict):
            print(f"[DEBUG] Response keys: {list(payload.keys())}")
            if "content" in payload:
                print(f"[DEBUG] content preview: {str(payload['content'])[:100]}...")
        else:
            print(f"[DEBUG] Response type: {type(payload).__name__}")

    def download(
        self,
        url: str,
        output_path: Path,
        *,
        headers: Optional[dict[str, str]] = None,
    ) -> int:
        try:
            with self.session.get(
                url,
                headers=headers,
                stream=True,
                timeout=DOWNLOAD_TIMEOUT,
            ) as response:
                response.raise_for_status()
                total = 0
                with output_path.open("wb") as file:
                    for chunk in response.iter_content(chunk_size=1024 * 128):
                        if chunk:
                            file.write(chunk)
                            total += len(chunk)
                return total
        except (requests.RequestException, OSError) as exc:
            raise ApiError(f"Gagal mengunduh file: {exc}") from exc


# ============================================================
# 05. API SERVICES
# ============================================================

class ToolService:
    """Seluruh integrasi API eksternal."""

    def __init__(self, http: Optional[HttpClient] = None) -> None:
        self.http = http or HttpClient()

    # -------------------- Magic Link -------------------------
    def send_magic_link(self, version: str, email: str) -> Any:
        if version == "v1":
            return self.http.request_json(
                "GET",
                V1_API_URL,
                params={"action": "send", "apikey": V1_API_KEY, "email": email},
            )
        if version == "v2":
            return self.http.request_json(
                "POST",
                V2_API_URL,
                json_data={"action": "send", "email": email},
            )
        raise ValueError(f"Method tidak dikenal: {version}")

    def verify_magic_link(self, version: str, email: str, link: str) -> Any:
        if version == "v1":
            return self.http.request_json(
                "GET",
                V1_API_URL,
                params={
                    "action": "verif",
                    "apikey": V1_API_KEY,
                    "email": email,
                    "url": link,
                },
            )
        if version == "v2":
            return self.http.request_json(
                "POST",
                V2_API_URL,
                json_data={"action": "verify", "email": email, "link": link},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "*/*",
                    "Origin": V2_ORIGIN,
                    "Referer": V2_REFERER,
                },
            )
        raise ValueError(f"Method tidak dikenal: {version}")

    # -------------------- Strom AI ---------------------------
    def ai_chat(
        self,
        prompt: str,
        *,
        session_id: Optional[str] = None,
        user_id: str = AI_CHAT_DEFAULT_USER_ID,
        image: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Any:
        return self.http.request_json(
            "POST",
            AI_CHAT_API_URL,
            json_data={
                "prompt": prompt,
                "sessionId": session_id,
                "image": image,
                "mimeType": mime_type,
                "userId": user_id,
                "mode": AI_CHAT_MODE,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": AI_CHAT_ORIGIN,
                "Referer": AI_CHAT_REFERER,
            },
        )

    # -------------------- Page Source ------------------------
    def get_page_source_token(self) -> str:
        payload = self.http.request_json(
            "GET",
            VPS_TOKEN_URL,
            headers={
                "Accept": "*/*",
                "Origin": VPS_ORIGIN,
                "Referer": VPS_REFERER,
            },
        )

        if not isinstance(payload, dict):
            raise ApiError("Response token tidak valid.")

        token = payload.get("token")
        if not isinstance(token, str) or not token.strip():
            raise ApiError("Token tidak ditemukan pada response.")
        return token.strip()

    def fetch_page_source(self, url: str, *, stylize: bool = True) -> Any:
        token = self.get_page_source_token()
        return self.http.request_json(
            "POST",
            VPS_FETCH_URL,
            json_data={"url": url, "token": token, "stylize": stylize},
            headers={
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": VPS_ORIGIN,
                "Referer": VPS_REFERER,
            },
        )

    # -------------------- Web -> ZIP --------------------------
    def web_to_zip(self, url: str) -> tuple[dict[str, Any], str]:
        try:
            response = self.http.session.post(
                ASPOSE_WEB_CONVERTER_URL,
                files={"link_303108836": (None, url)},
                headers={"Accept": "*/*", "Origin": ASPOSE_ORIGIN, "Referer": ASPOSE_REFERER},
                timeout=DOWNLOAD_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Gagal menghubungi Aspose: {exc}") from exc

        if response.status_code >= 400:
            raise ApiError(
                f"Aspose HTTP {response.status_code}: {response.text[:300]}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiError(
                f"Response Aspose bukan JSON: {response.text[:300]}"
            ) from exc

        if not isinstance(payload, dict):
            raise ApiError("Response Aspose tidak valid.")
        if not payload.get("IsSuccess"):
            raise ApiError(str(payload.get("Text") or "Konversi Web to ZIP gagal."))

        folder = payload.get("FolderName")
        filename = payload.get("FileName")
        if not isinstance(folder, str) or not folder.strip():
            raise ApiError("FolderName tidak ditemukan.")
        if not isinstance(filename, str) or not filename.strip():
            raise ApiError("FileName tidak ditemukan.")

        download_url = (
            f"{ASPOSE_WEB_DOWNLOAD_URL}/"
            f"{quote(folder.strip(), safe='')}"
            f"?file={quote(filename.strip(), safe='')}"
        )
        return payload, download_url

    # -------------------- TikTok ------------------------------
    def tiktok_info(self, url: str) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
            ),
        }
        try:
            response = self.http.session.get(
                TIKTOK_API_URL,
                params={"url": url},
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Gagal menghubungi API TikTok: {exc}") from exc

        if response.status_code >= 400:
            raise ApiError(
                f"API TikTok HTTP {response.status_code}: {response.text[:300]}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiError("Response API TikTok bukan JSON yang valid.") from exc

        if not isinstance(payload, dict) or not payload.get("status"):
            raise ApiError(
                str(payload.get("message") if isinstance(payload, dict) else None)
                or "API TikTok mengembalikan status gagal."
            )

        data = payload.get("data")
        if not isinstance(data, dict):
            raise ApiError("Field data dari API TikTok tidak valid.")

        result: dict[str, str] = {}
        for source_key, result_key in (
            ("no_watermark_link", "video_url"),
            ("no_watermark_link_hd", "video_hd_url"),
            ("music_link", "mp3_url"),
            ("author_nickname", "author"),
            ("text", "caption"),
            ("itemId", "item_id"),
            ("duration", "duration"),
            ("like_count", "like_count"),
            ("comment_count", "comment_count"),
            ("share_count", "share_count"),
            ("play_count", "play_count"),
        ):
            value = data.get(source_key)
            if value not in (None, ""):
                result[result_key] = str(value)

        if not result.get("video_url") and not result.get("video_hd_url"):
            raise ApiError("API tidak mengembalikan link video.")
        return result

    def download_media(self, url: str, output_path: Path, referer: str = TIKTOK_REFERER) -> int:
        return self.http.download(
            url,
            output_path,
            headers={
                "Accept": "*/*",
                "Referer": referer,
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
                ),
            },
        )

    # -------------------- Web -> APK --------------------------
    def create_web2apk(
        self,
        app_name: str,
        website_url: str,
        package_name: str,
        version_name: str,
        version_code: str,
        app_icon_url: str,
    ) -> Any:
        form = {
            "appName": app_name,
            "websiteUrl": website_url,
            "packageName": package_name,
            "versionName": version_name,
            "versionCode": version_code,
            "appIconUrl": app_icon_url,
        }
        try:
            response = self.http.session.post(
                WEB2APK_START_URL,
                files={key: (None, value) for key, value in form.items()},
                headers=WEB2APK_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise ApiError(f"Gagal membuat APK: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if response.status_code >= 400:
            raise ApiError(
                f"HTTP {response.status_code}: {extract_message(payload)}"
            )
        return payload

    def web2apk_status(self, build_id: str) -> Any:
        return self.http.request_json(
            "GET",
            WEB2APK_STATUS_URL,
            params={"build_id": build_id},
            headers=WEB2APK_HEADERS,
        )


# ============================================================
# 06. GENERIC HELPERS
# ============================================================

def open_in_browser(url: str) -> bool:
    try:
        if webbrowser.open(url, new=2):
            return True
    except Exception:
        pass

    try:
        system = platform.system().lower()
        if system == "windows":
            os.startfile(url)  # type: ignore[attr-defined]
            return True
        if system == "darwin":
            subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        if system == "linux":
            opener = shutil.which("xdg-open")
            if opener:
                subprocess.Popen([opener, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
    except Exception:
        pass
    return False


def show_result(payload: Any) -> bool:
    if is_success(payload):
        UI.success("Verifikasi berhasil.")
        code = extract_code_order(payload)
        if code:
            UI.success_box("CODE ORDER", code)
        return True

    UI.error(
        "Verifikasi gagal: "
        + extract_message(payload, "Verifikasi tidak dinyatakan berhasil oleh API.")
    )
    return False


def extract_ai_text(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("text", "content", "message", "response", "reply"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return extract_message(payload, "AI tidak mengembalikan teks jawaban.")


def extract_ai_session_id(payload: Any) -> Optional[str]:
    if isinstance(payload, dict):
        value = payload.get("sessionId")
        if value not in (None, ""):
            return str(value)
    return None


def extract_page_source_html(payload: Any) -> Optional[str]:
    if isinstance(payload, dict) and isinstance(payload.get("html"), str):
        return payload["html"]
    return None


def display_page_source_stats(payload: Any) -> None:
    if not isinstance(payload, dict):
        return

    page_info = payload.get("pageInfo")
    metrics = payload.get("metrics")
    server_info = payload.get("serverInfo")

    if isinstance(page_info, dict):
        UI.label(
            "Page",
            f"{page_info.get('totalSize', '?')} · "
            f"{page_info.get('totalChars', '?')} chars · "
            f"{page_info.get('totalWords', '?')} words · "
            f"{page_info.get('totalLines', '?')} lines",
        )
    if isinstance(metrics, dict):
        UI.label("Timing", f"{metrics.get('totalTime', '?')} ms")
    if isinstance(server_info, dict):
        UI.label(
            "Server",
            f"{server_info.get('server', '?')} · "
            f"HTTP {server_info.get('httpVersion', '?')} · "
            f"{server_info.get('httpCode', '?')}",
        )


def save_page_source(html: str, url: str) -> Optional[str]:
    try:
        host = urlparse(url).netloc or "page"
        safe_host = re.sub(r"[^a-zA-Z0-9._-]+", "_", host)
        suffix = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        output = Path(f"source_{safe_host}_{suffix}.html")
        output.write_text(html, encoding="utf-8")
        return str(output.resolve())
    except (OSError, ValueError):
        return None


def home(title: str, subtitle: str) -> None:
    UI.clear()
    UI.header(title, subtitle)


# ============================================================
# 07. FEATURE: MAGIC LINK
# ============================================================

def run_magic_link(service: ToolService, version: str) -> bool:
    config = V1 if version == "v1" else V2
    home("MAGIC LINK", config.label)

    UI.section("STEP 1 · EMAIL")
    email = prompt_required("Gmail", validate_email, "Format email tidak valid.")

    try:
        with Spinner("Mengirim magic link..."):
            send_result = service.send_magic_link(version, email)
    except ApiError as exc:
        UI.error(f"Gagal mengirim magic link: {exc}")
        return False

    # V1 secara eksplisit memakai status success pada response.
    if version == "v1" and not is_success(send_result):
        UI.error(extract_message(send_result, "Pengiriman magic link gagal."))
        return False

    UI.success("Permintaan magic link berhasil diproses.")
    UI.info("Periksa inbox Gmail Anda.")

    UI.section("STEP 2 · VERIFIKASI")
    UI.info("Salin URL magic link dari email Anda.")
    link = getpass.getpass(f"{C.CYAN}{'Magic link':<18} › {C.RESET}").strip()
    if not link:
        UI.error("URL magic link tidak boleh kosong.")
        return False

    try:
        with Spinner("Memverifikasi magic link..."):
            result = service.verify_magic_link(version, email, link)
    except ApiError as exc:
        UI.error(f"Gagal saat verifikasi: {exc}")
        return False

    print()
    return show_result(result)


def magic_link_menu(service: ToolService) -> bool:
    home("MAGIC LINK", "Alight Motion")
    UI.section("PILIH METODE")
    UI.menu_item("1", "V1", "GET · API lama")
    UI.menu_item("2", "V2", "POST · API baru")
    UI.menu_item("0", "KEMBALI", "Menu utama")

    choice = input(f"\n{C.CYAN}Pilih › {C.RESET}").strip()
    if choice == "1":
        return run_magic_link(service, "v1")
    if choice == "2":
        return run_magic_link(service, "v2")
    if choice == "0":
        return True

    UI.error("Pilihan tidak valid.")
    return False


# ============================================================
# 08. FEATURE: WEB TO APK
# ============================================================

def run_web2apk(service: ToolService) -> bool:
    home("WEB TO APK", "Website Builder")
    UI.section("PROJECT")

    app_name = prompt_required("Nama aplikasi")
    website_url = prompt_required("URL website", valid_url, "URL harus http:// atau https://.")
    package_name = prompt_required(
        "Package name",
        valid_package_name,
        "Contoh: com.nama.aplikasi",
    )
    version_name = prompt_required("Version name")
    version_code = prompt_required("Version code")
    app_icon_url = prompt_required(
        "URL icon",
        valid_url,
        "URL icon harus http:// atau https://.",
    )

    home("WEB TO APK", "Membangun aplikasi")
    UI.section("DETAIL PROJECT")
    UI.label("App", app_name)
    UI.label("Website", website_url)
    UI.label("Package", package_name)
    UI.label("Version", f"{version_name} ({version_code})")

    try:
        with Spinner("Membuat build APK..."):
            result = service.create_web2apk(
                app_name,
                website_url,
                package_name,
                version_name,
                version_code,
                app_icon_url,
            )
    except ApiError as exc:
        UI.error(str(exc))
        return False

    build_id = extract_build_id(result)
    if not build_id:
        UI.error("Build ID tidak ditemukan.")
        return False

    UI.success(f"Build dibuat · ID: {build_id}")
    UI.info("Menunggu proses build selesai...")

    download_url = extract_download_url(result)
    for _ in range(WEB2APK_MAX_POLLS):
        time.sleep(WEB2APK_POLL_INTERVAL)
        try:
            status_payload = service.web2apk_status(build_id)
        except ApiError:
            continue

        download_url = download_url or extract_download_url(status_payload)
        status = extract_status(status_payload)

        if download_url:
            break
        if status in {"failed", "error", "cancelled", "canceled"}:
            UI.error("Build APK gagal.")
            return False

    if not download_url:
        UI.error("Build belum selesai atau URL download tidak tersedia.")
        return False

    UI.success_box("APK SIAP", download_url)

    choice = input(f"\n{C.CYAN}Buka link di browser? [y/N] › {C.RESET}").strip().lower()
    if choice == "y":
        if open_in_browser(download_url):
            UI.success("Link dibuka di browser.")
        else:
            UI.warning("Browser tidak dapat dibuka otomatis. Salin link secara manual.")

    return True


# ============================================================
# 09. FEATURE: AI CHAT
# ============================================================

def run_ai_chat(service: ToolService) -> bool:
    home("STROM-AI", "Interactive Chat")
    UI.section("SESSION")
    user_id = input(
        f"{C.CYAN}{'User ID':<18} › {C.RESET}"
    ).strip() or AI_CHAT_DEFAULT_USER_ID

    session_id: Optional[str] = None
    UI.section("CHAT")
    UI.info("/exit = kembali · /clear = reset session")

    while True:
        try:
            prompt = input(f"{C.MAGENTA}{C.BOLD}You › {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            UI.warning("Chat dibatalkan.")
            return True

        if not prompt:
            continue

        command = prompt.lower()
        if command in {"/exit", "/quit", "/q"}:
            return True
        if command == "/clear":
            session_id = None
            UI.success("Session AI direset.")
            continue

        try:
            with Spinner("Strom-Ai sedang menjawab..."):
                payload = service.ai_chat(
                    prompt,
                    session_id=session_id,
                    user_id=user_id,
                )
        except ApiError as exc:
            UI.error(f"AI request gagal: {exc}")
            continue

        session_id = extract_ai_session_id(payload) or session_id
        answer = extract_ai_text(payload)

        print()
        print(f"{C.GREEN}{C.BOLD}Strom-Ai ›{C.RESET}")
        print(answer)
        print()

        if DEBUG and session_id:
            UI.info(f"[DEBUG] sessionId: {session_id}")


# ============================================================
# 10. FEATURE: PAGE SOURCE
# ============================================================

def run_page_source(service: ToolService) -> bool:
    home("PAGE SOURCE", "View Page Source")
    UI.section("INPUT")
    url = prompt_required(
        "URL website",
        valid_url,
        "URL harus http:// atau https://.",
    )

    home("PAGE SOURCE", "Mengambil source")
    UI.label("URL", url)

    try:
        with Spinner("Mengambil token dan page source..."):
            payload = service.fetch_page_source(url, stylize=True)
    except ApiError as exc:
        UI.error(f"Gagal mengambil source: {exc}")
        return False

    html = extract_page_source_html(payload)
    if html is None:
        UI.error("Response tidak berisi field 'html'.")
        if DEBUG:
            print(payload)
        return False

    UI.success("Page source berhasil diambil.")
    UI.section("STATISTIK")
    display_page_source_stats(payload)

    try:
        choice = input(
            f"\n{C.CYAN}Simpan HTML ke file? [Y/n] › {C.RESET}"
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return True

    if choice in ("", "y", "yes"):
        saved = save_page_source(html, url)
        if saved:
            UI.success(f"HTML disimpan: {saved}")
            return True
        UI.error("Gagal menyimpan HTML ke file.")
        return False

    UI.section("PREVIEW")
    print(html[:5000])
    if len(html) > 5000:
        UI.info(f"... {len(html) - 5000} karakter lainnya tidak ditampilkan.")
    return True


# ============================================================
# 11. FEATURE: WEB TO ZIP
# ============================================================

def run_web_to_zip(service: ToolService) -> bool:
    home("WEB TO ZIP", "Website Packager")
    UI.section("INPUT")
    url = prompt_required(
        "URL website",
        valid_url,
        "URL harus http:// atau https://.",
    )

    try:
        with Spinner("Mengonversi website ke ZIP..."):
            payload, download_url = service.web_to_zip(url)

        filename = str(payload.get("FileName", "website.zip"))
        UI.success("Konversi selesai.")
        UI.label("File", filename)
        UI.label("Status", str(payload.get("Status", "Complete")))

        custom = input(
            f"\n{C.CYAN}{'Nama output':<18} › {C.RESET}"
            f"[{filename}] "
        ).strip()
        output_name = custom or filename
        if not output_name.lower().endswith(".zip"):
            output_name += ".zip"

        with Spinner("Mengunduh ZIP..."):
            response = service.http.session.get(
                download_url,
                headers={"Accept": "application/zip,*/*", "Referer": ASPOSE_REFERER},
                timeout=DOWNLOAD_TIMEOUT,
            )
            response.raise_for_status()

        data = response.content
        content_type = response.headers.get("content-type", "")
        if "zip" not in content_type.lower() and not data.startswith(b"PK"):
            raise ApiError(
                "Response download bukan ZIP. "
                f"Content-Type: {content_type or 'unknown'}"
            )

        output = Path(output_name)
        output.write_bytes(data)
        UI.success(f"ZIP tersimpan: {output.resolve()}")
        UI.info(f"Ukuran: {len(data):,} bytes")
        return True

    except (ApiError, requests.RequestException, OSError) as exc:
        UI.error(f"Web to ZIP gagal: {exc}")
        return False


# ============================================================
# 12. FEATURE: TIKTOK DOWNLOADER
# ============================================================

def run_tiktok_dl(service: ToolService) -> bool:
    home("TIKTOK DOWNLOADER", "Public Media Downloader")
    UI.section("INPUT")
    url = prompt_required(
        "URL TikTok",
        valid_tiktok_url,
        "Masukkan URL TikTok yang valid.",
    )

    try:
        with Spinner("Memproses link TikTok..."):
            info = service.tiktok_info(url)

        UI.section("VIDEO INFO")
        for key, label in (
            ("author", "Author"),
            ("caption", "Caption"),
            ("like_count", "Likes"),
            ("play_count", "Views"),
        ):
            if info.get(key):
                value = info[key]
                if key == "caption":
                    value = value[:180]
                UI.label(label, value)

        choices: list[tuple[str, str, str, str]] = []
        if info.get("video_url"):
            choices.append(("1", "MP4", info["video_url"], ".mp4"))
        if info.get("video_hd_url"):
            choices.append(("2", "MP4 HD", info["video_hd_url"], ".mp4"))
        if info.get("mp3_url"):
            choices.append(("3", "MP3", info["mp3_url"], ".mp3"))

        UI.section("FORMAT")
        for key, label, _, _ in choices:
            UI.menu_item(key, label)

        choice = input(f"\n{C.CYAN}Pilih format [1] › {C.RESET}").strip() or "1"
        selected = next((item for item in choices if item[0] == choice), None)
        if not selected:
            UI.error("Pilihan format tidak valid.")
            return False

        _, label, media_url, extension = selected
        default_name = f"tiktok_{int(time.time())}{extension}"
        custom = input(
            f"{C.CYAN}{'Nama output':<18} › {C.RESET}[{default_name}] "
        ).strip()
        output_name = custom or default_name
        if not output_name.lower().endswith(extension):
            output_name += extension

        output_path = Path(output_name)
        with Spinner(f"Mengunduh {label}..."):
            size = service.download_media(media_url, output_path)

        UI.success(f"{label} tersimpan: {output_path.resolve()}")
        UI.info(f"Ukuran: {size:,} bytes")
        return True

    except (ApiError, requests.RequestException, OSError) as exc:
        UI.error(f"TikTok download gagal: {exc}")
        return False


# ============================================================
# 13. CATEGORY MENUS
# ============================================================

def web_tools_menu(service: ToolService) -> bool:
    while True:
        home("WEB TOOLS", "Web Automation")
        UI.section("FITUR")
        UI.menu_item("1", "WEB TO APK", "Build website menjadi APK")
        UI.menu_item("2", "PAGE SOURCE", "Ambil HTML/source halaman")
        UI.menu_item("3", "WEB TO ZIP", "Pack website menjadi ZIP")
        UI.menu_item("0", "KEMBALI", "Menu utama")

        choice = input(f"\n{C.CYAN}Pilih › {C.RESET}").strip()
        if choice == "1":
            return run_web2apk(service)
        if choice == "2":
            return run_page_source(service)
        if choice == "3":
            return run_web_to_zip(service)
        if choice == "0":
            return True
        UI.error("Pilihan tidak valid.")
        time.sleep(0.6)


def ai_tools_menu(service: ToolService) -> bool:
    return run_ai_chat(service)


def downloader_menu(service: ToolService) -> bool:
    return run_tiktok_dl(service)


# ============================================================
# 14. MAIN MENU
# ============================================================

@dataclass(frozen=True)
class MenuRoute:
    title: str
    description: str
    handler: Callable[[ToolService], bool]


ROUTES = {
    "1": MenuRoute("MAGIC LINK", "Alight Motion V1 / V2", magic_link_menu),
    "2": MenuRoute("WEB TOOLS", "Web TO APK / Source / ZIP", web_tools_menu),
    "3": MenuRoute("AI TOOLS", "Strom-Ai interactive chat", ai_tools_menu),
    "4": MenuRoute("DOWNLOADER", "TikTok public media", downloader_menu),
}


def main_menu() -> Optional[str]:
    home("PROJECT-LEVIATHAN", f"Toolkit v{APP_VERSION}")
    UI.section("CATEGORY MENU")

    for key, route in ROUTES.items():
        UI.menu_item(key, route.title, route.description)
    UI.menu_item("0", "EXIT", "Tutup aplikasi")

    choice = input(f"\n{C.CYAN}Pilih kategori › {C.RESET}").strip()
    return choice


def main() -> None:
    startup()
    service = ToolService()

    while True:
        try:
            selected = main_menu()
        except (EOFError, KeyboardInterrupt):
            print()
            UI.warning("Dibatalkan oleh pengguna.")
            return

        if selected == "0":
            UI.clear()
            UI.header("PROJECT-LEVIATHAN", "Session closed")
            UI.success("Program ditutup.")
            return

        route = ROUTES.get(selected)
        if route is None:
            UI.error("Pilihan kategori tidak valid.")
            time.sleep(0.7)
            continue

        try:
            success = route.handler(service)
        except KeyboardInterrupt:
            print()
            UI.warning("Operasi dibatalkan.")
            success = False
        except Exception as exc:  # safety net agar menu tidak mati total
            UI.error(f"Unexpected error: {exc}")
            if DEBUG:
                raise
            success = False

        print()
        if success:
            UI.success_box("DONE", "Operation completed successfully.")
        else:
            UI.warning("Operation incomplete.")

        try:
            again = input(
                f"\n{C.CYAN}Kembali ke menu utama? [Y/n] › {C.RESET}"
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if again not in ("", "y", "yes"):
            UI.clear()
            UI.header("PROJECT-LEVIATHAN", "Session closed")
            UI.info("Program ditutup.")
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Dibatalkan oleh pengguna.{C.RESET}")
        sys.exit(130)
