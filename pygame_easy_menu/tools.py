from pathlib import Path

ICON = Path(__file__).parent.absolute() / "assets" / "icon.png"
BG = Path(__file__).parent.absolute() / "assets" / "background.png"

__all__ = ["BG","ICON"]