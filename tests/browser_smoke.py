"""Exercise the published tool at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.wait_for_selector("#content:visible")
                assert "132,603" in page.locator(".big").first.inner_text()
                page.select_option("#left","2021A00055915002")
                assert "28,963" in page.locator(".big").first.inner_text()
                page.select_option("#topic","Housing")
                assert page.locator("#table tbody tr").count()>=4
                page.fill("#find1","an unmatched place name")
                assert page.locator("#download").is_disabled()
                page.fill("#find1","Langley")
                page.select_option("#left","2021A00055915001")
                assert not page.locator("#download").is_disabled()
                with page.expect_download():
                    page.click("#download")
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, published values, filters and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
