# pollyvent/yvent/layouts/__init__.py

from .diagonal import DiagonalLayout
from .centered import CenteredLayout
from .minimal import MinimalLayout

LAYOUT_REGISTRY = {
    "diagonal": DiagonalLayout,
    "centered": CenteredLayout,
    "minimal": MinimalLayout
    }

def get_layout(name: str):
    layout_class = LAYOUT_REGISTRY.get(name.lower())
    if layout_class is None:
        raise ValueError(f"No such layout: '{name}'")
    return layout_class()

