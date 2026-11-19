# Architecture

The Python `Blockchain` owns accounts, pending transactions and the authoritative in-memory block list. Each block hash is SHA-256 over canonical JSON (`sort_keys=True`, compact separators) of every block field except `hash`. The database stores JSON snapshots through SQLAlchemy Core; startup rebuilds block objects and revalidates hashes and previous-hash links before accepting the snapshot.

FastAPI exposes REST operations and `/ws`. The network manager models full, miner and validator nodes in-process. The React application polls read models for resilient UI updates and also maintains a WebSocket connection indicator/event refresh. The 3D view renders the same node records exposed by `/api/statistics`; the 2D view provides an accessible fallback.

`Transport` seam: the `Network` manager is deliberately isolated from the blockchain engine. A future adapter can replace its in-process synchronization calls with HTTP, gRPC, or libp2p delivery without changing block serialization or validation.
