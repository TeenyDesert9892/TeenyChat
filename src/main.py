from ui.main_ui import main
from utils.utils import *

import flet as ft

import os

os.environ["FLET_SECRET_KEY"] = secret_key_generator(32)
os.environ["FLET_SERVER_PORT"] = "9892"

os.environ["FLET_ASSETS_DIR"] = os.path.normpath(f"{os.getcwd()}/src/assets")
os.environ["FLET_UPLOAD_DIR"] = os.path.normpath(f"{os.getcwd()}/src/upload")

if __name__ == "__main__":
    ft.app(main)