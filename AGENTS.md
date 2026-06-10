# AI Coding Agent Guide for beautify_report

## Purpose
This repository implements a supply-chain report beautification system using Python, NiceGUI, FastAPI, and database access layers. It is primarily a web application with a UI built in `pages/` and `components/`, backed by DAOs in `dao/` and database adapters in `db/`.

## Entry points and run commands
- Primary application entry point: `main.py`
- Start locally: `python main.py`
- Docker build/run:
  - `docker build -t beautify_report .`
  - `docker run --rm -it beautify_report:latest`

## Testing
- The existing tests use Python `unittest`.
- Run tests with:
  - `python -m unittest discover -s tests`

## Key directories
- `pages/` - NiceGUI page definitions and route handlers
- `components/` - reusable UI components and helpers
- `dao/` - data access objects and persistence logic
- `db/` - database adapters for MySQL and MongoDB
- `utils/` - application helpers, OCR manager, upload helpers, global state
- `grpc_protoc/` - generated gRPC client code; do not modify generated files directly
- `cfg/` - configuration files such as `beautify_report.cfg` and `log.yaml`
- `static/` - fonts, images, uploads and other static assets
- `resources/strings.py` - application strings and localization values

## Project conventions
- UI logic lives in `pages/` and often uses NiceGUI components contained in `components/`
- Business logic and database access is separated into `dao/` and `db/`
- Comments and documentation are often written in Chinese; maintain Chinese meaning when editing or translating code comments
- Keep generated gRPC files under `grpc_protoc/` untouched unless regeneration is explicitly needed

## Important behavior notes
- `main.py` registers auth middleware for `/login`, `/api`, `/static`, and NiceGUI routes
- `main.py` initializes logging from `cfg/log.yaml` and filters `ClientDisconnect` exceptions
- The app uses NiceGUI and FastAPI together: NiceGUI creates pages while FastAPI handles API routes
- Global state is exposed via `utils/global_vars.py`

## Useful files
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker build/runtime environment
- `cfg/log.yaml` - logging configuration
- `main.py` - app initialization and routing

## Notes for AI agents
- Prefer small, focused changes over broad refactors unless the repo clearly needs large architecture updates
- Preserve existing Chinese descriptive comments and business terms
- When adding or changing routes or UI pages, update the corresponding `pages/` and `components/` modules together
- Avoid changing generated code in `grpc_protoc/` unless the user asks for gRPC regeneration

## Suggested future customizations
- Add a custom skill for `NiceGUI` page generation and validation
- Add an instruction for database adapter patterns in `dao/` and `db/`
- Add a hook for identifying and preserving Chinese comment translations
