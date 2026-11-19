# API quick reference

Base path: `/api` (interactive OpenAPI docs at `/docs`). Errors use FastAPI's JSON detail response.

- `GET /health`, `GET /statistics`
- `GET /blockchain`, `GET /blockchain/validate`, `GET /blockchain/block/{index}`
- `GET|POST /transactions`
- `GET /mining/status`, `POST /mining/start`, `POST /mining/pause`, `POST /mining/cancel`
- `GET|POST /nodes`, `DELETE /nodes/{id}`, `POST /nodes/{id}/{activate|deactivate|validate|fail|recover}`
- `POST /network/{simulate|synchronize|reset}`
- `POST /security/{tamper|reset-sandbox}`
- `GET /activity`, `GET /export`, `GET|POST /learning/progress`
- WebSocket: `/ws`; messages use `{type,timestamp,payload}`.
