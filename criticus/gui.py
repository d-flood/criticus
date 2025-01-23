import asyncio
import ctypes
import platform
import re
import socket
import sys
import threading
import time
import unicodedata
from pathlib import Path

import toga
from toga.style.pack import COLUMN, Pack
from uvicorn import Config, Server

if platform.system() == "Windows":
    # Set DPI awareness for higher resolution screens
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        print("DPI awareness could not be set")


def normalize_greek(text: str):
    """Remove diacritics, accents, punctuation, and any other combining characters."""
    text = "".join([unicodedata.normalize("NFD", letter)[0] for letter in text])
    text = text.lower()
    text = re.sub(r',|·|\.|;|:|!|\?|»|-|- |\'|"|᾽', "", text)
    text = re.sub(r" +", " ", text)
    return text


class Criticus(toga.App):
    def __init__(self, *args, local_port=8000, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_port = local_port

    def startup(self):
        self.main_window = toga.MainWindow(size=(768, 700))

        self.webview = toga.WebView(style=Pack(flex=1))

        box = toga.Box(
            children=[
                self.webview,
            ],
            style=Pack(direction=COLUMN),
        )

        self.main_window.content = box
        self.webview.url = f"http://localhost:{self.local_port}/"

        # Show the main window
        self.main_window.show()

    async def on_running(self):
        while True:
            task: dict[str, str] | None = await self.webview.evaluate_javascript(
                "getTask()"
            )
            if not task:
                await asyncio.sleep(0.5)
                continue
            if task.get("name") == "pick_directory":
                directory = await self.pick_directory()
                if directory:
                    directory = Path(directory).as_posix()
                    self.webview.evaluate_javascript(
                        f"setInputValue('{directory}', '{task.get('target')}')"
                    )
            elif task.get("name") == "pick_file":
                file = await self.pick_file(task.get("ext", "txt"))
                if file:
                    file = Path(file).as_posix()
                    self.webview.evaluate_javascript(
                        f"setInputValue('{file}', '{task.get('target')}')"
                    )
            elif task.get("name") == "new_file":
                file = await self.new_file(task.get("ext", "txt"))
                if file:
                    file = Path(file).as_posix()
                    self.webview.evaluate_javascript(
                        f"setInputValue('{file}', '{task.get('target')}')"
                    )
            elif task.get("name") == "normalize":
                text = normalize_greek(task.get("value"))
                self.webview.evaluate_javascript(
                    f"setInputValue('{text}', '{task.get('target')}')"
                )

    async def pick_directory(self):
        dialog = toga.SelectFolderDialog(
            title="Select a directory",
        )
        directory = await self.main_window.dialog(dialog)
        return directory

    async def pick_file(self, ext: str = "txt"):
        dialog = toga.OpenFileDialog(
            title="Select a file",
            file_types=[ext],
        )
        file = await self.main_window.dialog(dialog)
        return file

    async def new_file(self, ext: str):
        dialog = toga.SaveFileDialog(
            title="Save file as",
            file_types=[ext],
            suggested_filename=f"transcription.{ext}",
        )
        file = await self.main_window.dialog(dialog)
        return file


async def serve(port: int):
    # Get the directory containing gui.py
    base_dir = Path(__file__).parent
    # Add the base directory to Python path so Uvicorn can find the web module
    sys.path.insert(0, str(base_dir))

    config = Config(
        "web.asgi:application",
        port=port,
    )
    server = Server(config=config)
    await server.serve()


def run_server(port: int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(serve(port))


def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find first available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find free port after {max_attempts} attempts")


def main():
    try:
        port = find_free_port()
        server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
        server_thread.start()

        # Give the server a moment to start
        time.sleep(1)

        app = Criticus(
            "Criticus",
            "com.davidaflood.criticus",
            home_page="https://github.com/d-flood/criticus",
            local_port=port,
        )
        app.main_loop()
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
