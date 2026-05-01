"""
Shared preview / export helper for every part module's __main__ block.

Each part module ends with:

    if __name__ == "__main__":
        from preview import preview
        preview({"left_side": left_side})

The helper:
  - writes <project_root>/build/<stem>.step / .stl gated on cfg.EXPORT_STEP /
    EXPORT_STL,
  - prints a compact bounding-box + volume line per part,
  - calls ocp_vscode.show(...) gated on cfg.SHOW_IN_VIEWER (with ImportError
    fallback so headless runs do not crash).

Behaviour matches what CLAUDE.md mandates for every part module's __main__
block - extend this helper if a new behaviour is needed, do not re-implement
the pipeline inline.
"""

from pathlib import Path

from build123d import Compound, Part, export_step, export_stl

import config as cfg

_PROJECT_ROOT = Path(__file__).resolve().parent
_BUILD_DIR = _PROJECT_ROOT / "build"


def preview(parts: dict[str, Part | Compound]) -> None:
    """Export + bbox-print + viewer call for one or more parts.

    parts : ordered dict of {filename_stem: Part}. The stem is used as the
            file name for STEP/STL exports and as the label in show().
    """
    if cfg.EXPORT_STEP or cfg.EXPORT_STL:
        _BUILD_DIR.mkdir(exist_ok=True)
        for name, part in parts.items():
            if cfg.EXPORT_STEP:
                step_path = _BUILD_DIR / f"{name}.step"
                export_step(part, str(step_path))
                print(f"{name} STEP -> {step_path}")
            if cfg.EXPORT_STL:
                stl_path = _BUILD_DIR / f"{name}.stl"
                export_stl(part, str(stl_path))
                print(f"{name} STL  -> {stl_path}")

    name_w = max((len(n) for n in parts), default=0)
    for name, part in parts.items():
        bb = part.bounding_box()
        bb_min = tuple(round(v, 2) for v in tuple(bb.min))
        bb_max = tuple(round(v, 2) for v in tuple(bb.max))
        print(f"{name:<{name_w}}  bb={bb_min}->{bb_max}  vol={part.volume:.1f}")

    if cfg.SHOW_IN_VIEWER:
        try:
            from ocp_vscode import show
        except ImportError:
            print("ocp_vscode not available - skipping show()")
        else:
            show(*parts.values(), names=list(parts.keys()))
