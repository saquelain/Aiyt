"""Every Short format. Each module has make(out_path, seed, **opts) -> meta dict
with length_s, params, title, tags and hashtags."""
import importlib

FORMATS = ["emoji_math", "odd_emoji", "stop_timer", "afterimage", "color_word", "marble_race"]


def get(name):
    if name not in FORMATS:
        raise SystemExit(f"unknown format {name}; have {', '.join(FORMATS)}")
    return importlib.import_module(f"{__name__}.{name}")
