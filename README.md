# BLOCKLAB 360 — Interactive Blockchain Network Simulator

A working educational blockchain lab: a Python SHA-256 proof-of-work engine, FastAPI REST + WebSocket service, SQLite persistence, simulated peer network, and a React + Three.js control-room UI.

> **Educational simulation only.** Networking is simulated in-process; nodes are records in one process, not real network peers. Consensus is simplified proof-of-work + longest-valid-chain selection, not production BFT. There is no Sybil resistance, real finality, economic security, or production wallet/signature system. Do not use this as a cryptocurrency or financial system.

## Features
- Deterministic canonical JSON and real SHA-256 block hashes.
- Configurable proof-of-work difficulty (1–6 leading hexadecimal zeroes).
- Accounts, pending transaction balance checks, double-spend prevention, block mining.
- Five sample nodes (full/miner/validator), node lifecycle controls, synchronization and health.
- Tamper experiment on a deep-copied sandbox; original chain remains intact.
- SQLite snapshot persistence with integrity revalidation on startup; `DATABASE_URL` can point to PostgreSQL.
- REST API, `/ws` event channel, exportable JSON, 3D/2D topology, ledger explorer, audit and learning panels.
- Responsive warm-minimal UI. 2D view is the accessible low-power alternative to WebGL.

## Requirements
- Python 3.12 recommended (the code also runs on newer Python versions).
- Node.js 20+ and npm.
- Windows PowerShell, macOS, or Linux.

## Windows PowerShell setup
Open two terminals in the project root.

### 1. Backend
```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API docs: http://127.0.0.1:8000/docs

### 2. Frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. The frontend connects to `http://127.0.0.1:8000` by default. To change it, create `frontend/.env` with `VITE_API_URL=http://127.0.0.1:8000`.

### 3. Tests and production build
```powershell
# Backend
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q

# Frontend
cd ..\frontend
npm test
npm run build
```

## Quick demo (about 5 minutes)
1. Open Overview and inspect the five seeded simulated nodes.
2. Open Transaction Pool. Transfer 25 from `alice` to `bob` and broadcast it.
3. Open Mining Lab. Choose difficulty 3 and start mining with the active miner node. Watch nonce/hash-rate telemetry; the mined block appears in the Explorer.
4. Open Consensus Monitor and synchronize active peers to the new block height.
5. Open Security & Audit. Choose block 1 (or another non-genesis block) and run the tamper experiment. The sandbox validation reports the first broken block while the original ledger remains valid.
6. Reset the sandbox, export the network JSON, then open Learning Lab and verify a lesson against backend state.

## Project structure
```text
BLOCKLAB-360/
├── backend/app/{blockchain,network,api,database,services,websocket}/
├── backend/tests/
├── frontend/src/{components,pages,scenes,hooks,services,store,types}/
├── docs/{architecture.md,consensus.md,api.md,learning-design.md}
└── scripts/{setup.ps1,run-dev.ps1,test-all.ps1}
```

## Notes and limitations
- The engine is the source of truth. Persisted snapshots are reloaded only after recomputing all hashes and links; invalid snapshots are discarded.
- Mining runs in a background thread. Cancel/pause requests stop safely at the worker's cancellation check; this first version treats pause as a safe stop rather than preserving a resumable nonce session.
- A block is mined from the current pending pool. The educational consensus model synchronizes active node heights to the canonical chain; it does not implement adversarial fork races or network partition consensus.
- The frontend uses real backend data for counters and node topology. It has a 3D R3F scene and a functional 2D fallback.
- The sample chain starts with a genesis block. Add transactions and mine blocks to grow it; the project intentionally avoids fabricated historical transactions or hashes.
