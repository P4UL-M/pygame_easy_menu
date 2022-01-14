from pathlib import Path
import pygame_easy_menu.path as _module

ICON = Path(_module.__file__).absolute() / "assets" / "icon.png"
BG = Path(_module.__file__).absolute() / "assets" / "bg.png"


__all__ = ["ICON","BG"]