import asyncio
import ctypes
import platform
import re
import unicodedata
from pathlib import Path

import toga
from toga.style.pack import COLUMN, Pack

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


def main():
    app = Criticus(
        "Criticus",
        "com.davidaflood.criticus",
        home_page="https://github.com/d-flood/criticus",
        local_port=8000,
    )
    app.main_loop()


if __name__ == "__main__":
    main()
