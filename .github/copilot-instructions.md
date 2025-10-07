# Copilot Instructions for Beryllium

## Project Overview
- **Beryllium** is a 4X/strategy game built with Python and [arcade](https://api.arcade.academy/en/latest/), featuring a galaxy simulation, nation management, and a modular UI.
- The architecture is split into **model** (simulation, data, logic) and **views** (UI, rendering, user interaction).
- The simulation is driven by a `GameModel` (see `model/model.py`), which manages the galaxy, nations, and the game calendar.
- The main entry point is `main.py`, which initializes the model, assets, persistent UI, and launches the main `GalaxyView`.

## Key Components
- `model/` — Core simulation logic:
  - `model.py`: Central game state and update loop
  - `world/galaxy.py`: Galaxy generation, star/solar system placement, hyperlane graph
  - `politics/nation.py`: Nation simulation and monthly/daily update hooks
  - `assets.py`: Asset loading (UI art, icons, portraits)
- `views/` — UI and rendering:
  - `galaxy_view.py`: Main galaxy map, overlays, camera, and user input
  - `ui_stuff.py`: Persistent HUD and resource bar
  - `UI_stuff/planet_menu.py`: Planet interface (WIP)
- `assets/` — Art, icons, portraits, music, and sound

## Patterns & Conventions
- **Observer Pattern**: The `Calendar` notifies observers (UI, nations) for daily/monthly updates.
- **Asset Management**: Use `AssetManager` for all asset loading; access via `window.asset_manager`.
- **UI**: All UI is built with `arcade.gui`; persistent UI is attached to the window as `window.persistent_ui`.
- **Naming**: Lowercase for files, PascalCase for classes, snake_case for variables/functions.
- **Map Overlays**: Add overlays to the `maps` dict in `GalaxyView`.

## Developer Workflows
- **Run the game**: `python main.py`
- **Dependencies**: Requires `arcade`, `scipy`, `networkx` (install via pip)
- **Debugging**: Print statements are used for debugging; no formal logging yet.
- **Testing**: No formal test suite; manual testing via running the game.

## Integration & Extensibility
- To add new UI panels, extend `PersistentUI` or add new views in `views/`.
- To add new simulation logic, extend `GameModel` or add new modules under `model/`.
- To add assets, place files in the appropriate `assets/` subfolder and update `AssetManager` if needed.

## Examples
- To add a new monthly-updating system, register it as an observer to `Calendar`.
- To add a new map overlay, add it to the `maps` dict in `GalaxyView`.

---
For questions, see the referenced files above for working examples of each pattern.
