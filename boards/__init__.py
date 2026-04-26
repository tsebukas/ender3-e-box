"""Per-board / per-board-set panel configurations for the e-box project.

Each module here wires one or more electronics boards onto panel
blanks: imports the relevant blank(s) from `panels`, the board's
intrinsic data from a root-level `config_<board>.py`, and applies
mount-hole bosses, connector cutouts, etc. via `panel_features`.
The result is a configured Part exposed at module level for
`assembly.py` (or a build script) to import.
"""
