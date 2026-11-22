from __future__ import annotations
import asyncio, time, json, threading
from contextlib import asynccontextmanager
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .blockchain.engine import Blockchain, Block, Transaction
from .network.manager import Network
from .database.db import init_db, save_snapshot, load_snapshot

class TxIn(BaseModel): sender:str; receiver:str; amount:float=Field(gt=0); description:str=""
class MineIn(BaseModel): miner_id:str="miner-01"; difficulty:int=Field(default=3,ge=1,le=6)
class NodeIn(BaseModel): type:str=Field(default="full",pattern="^(full|miner|validator)$")
class TamperIn(BaseModel): index:int=Field(gt=0)
class SimIn(BaseModel): latency_ms:int=Field(default=40,ge=0,le=5000); drop_rate:float=Field(default=0,ge=0,le=1)

@asynccontextmanager
async def lifespan(app:FastAPI):
    global chain, event_loop
    event_loop = asyncio.get_running_loop()
    init_db()
    snapshot = load_snapshot()
    if snapshot:
        try:
            chain.chain = [Block(**item) for item in snapshot.get("chain", [])]
            chain.pending = [Transaction(**item) for item in snapshot.get("pending", [])]
            chain.accounts = snapshot.get("accounts", chain.accounts)
            chain.difficulty = snapshot.get("difficulty", chain.difficulty)
            if not chain.validate()["valid"]: chain = Blockchain()
        except Exception:
            chain = Blockchain()
    else:
        # Seed nine genuine, low-difficulty demonstration blocks (not fabricated hashes).
        accounts = list(chain.accounts)
        for i in range(9):
            sender = accounts[i % len(accounts)]
            receiver = accounts[(i + 1) % len(accounts)]
            chain.add_transaction(sender, receiver, 1.0, f"Sample ledger transfer {i + 1}")
            chain.mine_pending("miner-01", difficulty=1)
        network.sync(chain.height)
        save_snapshot(chain.export())
    yield
app=FastAPI(title="BLOCKLAB 360 API",version="1.0.0",lifespan=lifespan)
import os

DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://blocklab-360.vercel.app",
]

FRONTEND_ORIGINS = DEFAULT_ORIGINS + [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_ORIGIN", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(dict.fromkeys(FRONTEND_ORIGINS)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chain=Blockchain(); network=Network(); activity=[]; clients=set(); mining={"running":False,"paused":False,"attempts":0,"hash_rate":0.0,"elapsed":0.0,"candidate_hash":"","miner_id":None,"result":None}; mining_cancel=threading.Event(); sandbox=None; event_loop=None

def log(event,detail):
    item={"time":time.time(),"event":event,"detail":detail}; activity.insert(0,item); del activity[100:]
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast(event, item), event_loop)
async def broadcast(kind,payload):
    message={"type":kind,"timestamp":time.time(),"payload":payload}
    dead=[]
    for ws in list(clients):
        try: await ws.send_json(message)
        except Exception: dead.append(ws)
    for ws in dead: clients.discard(ws)
def stats():
    ns=network.stats(); return {**ns,"total_transactions":len(chain.pending)+sum(len(b.transactions) for b in chain.chain[1:]),"pending_transactions":len(chain.pending),"block_height":chain.height,"health":"healthy" if chain.validate()["valid"] and ns["failed_nodes"]==0 else "attention","mining":mining.copy()}
def persist(): save_snapshot(chain.export())

@app.get("/api/health")
def health(): return {"status":"ok","service":"BLOCKLAB 360","chain_valid":chain.validate()["valid"],"network":"simulated in-process"}
@app.get("/api/statistics")
def statistics(): return stats()
@app.get("/api/blockchain")
def blockchain(): return {"height":chain.height,"blocks":[asdict(b) for b in chain.chain],"validation":chain.validate(),"accounts":chain.accounts}
@app.get("/api/blockchain/validate")
def validate(): return chain.validate()
@app.get("/api/blockchain/block/{index}")
def block(index:int):
    if index<0 or index>=len(chain.chain): raise HTTPException(404,"Block not found")
    return asdict(chain.chain[index])
@app.get("/api/transactions")
def transactions(): return {"pending":[asdict(t) for t in chain.pending],"confirmed":[tx for b in chain.chain[1:] for tx in b.transactions],"rejected":[]}
@app.post("/api/transactions",status_code=201)
async def create_tx(body:TxIn):
    try: tx=chain.add_transaction(body.sender,body.receiver,body.amount,body.description)
    except ValueError as e: raise HTTPException(400,str(e))
    log("transaction.broadcast",f"{tx.sender} → {tx.receiver}: {tx.amount:g}"); await broadcast("transaction.broadcast",asdict(tx)); persist(); return asdict(tx)

def mine_worker(miner,difficulty):
    global mining
    mining_cancel.clear(); mining.update(running=True,paused=False,attempts=0,hash_rate=0.0,elapsed=0.0,candidate_hash="",miner_id=miner,result=None)
    try:
        def progress(attempts,elapsed,digest):
            mining.update(attempts=attempts,elapsed=elapsed,hash_rate=attempts/max(elapsed,1e-9),candidate_hash=digest)
            if event_loop and event_loop.is_running():
                asyncio.run_coroutine_threadsafe(broadcast("mining.progress", mining.copy()), event_loop)
        b,attempts,elapsed=chain.mine_pending(miner,difficulty,mining_cancel.is_set,progress)
        mining.update(running=False,attempts=attempts,elapsed=elapsed,hash_rate=attempts/max(elapsed,1e-9),candidate_hash=b.hash,result={"success":True,"block":b.index,"hash":b.hash})
        network.sync(chain.height); log("block.created",f"Block #{b.index} mined by {miner}"); persist()
    except InterruptedError: mining.update(running=False,paused=False,result={"success":False,"message":"Mining cancelled"})
    except Exception as e: mining.update(running=False,result={"success":False,"message":str(e)})
@app.post("/api/mining/start")
def start_mining(body:MineIn):
    if mining["running"]: raise HTTPException(409,"Mining is already running")
    if not chain.pending: raise HTTPException(400,"Add a transaction before mining")
    node=network.get(body.miner_id)
    if not node or node.type!="miner" or node.status!="active": raise HTTPException(400,"Select an active miner node")
    t=threading.Thread(target=mine_worker,args=(body.miner_id,body.difficulty),daemon=True); t.start(); return {"started":True,"miner_id":body.miner_id,"difficulty":body.difficulty}
@app.post("/api/mining/pause")
def pause_mining():
    # Pause is represented as a cooperative cancellation boundary; pending transactions remain safe.
    if not mining["running"]: return {"paused":False,"message":"Mining is not running"}
    mining_cancel.set(); return {"paused":True,"message":"Mining stopping safely; pending transactions are retained"}
@app.post("/api/mining/cancel")
def cancel_mining(): mining_cancel.set(); return {"cancel_requested":True}
@app.get("/api/mining/status")
def mining_status(): return mining
@app.get("/api/nodes")
def nodes(): return network.stats()
@app.post("/api/nodes",status_code=201)
def add_node(body:NodeIn):
    n=network.add(body.type); log("node.status",f"Added {n.id}"); return asdict(n)
@app.delete("/api/nodes/{node_id}")
def remove_node(node_id:str):
    n=network.get(node_id)
    if not n: raise HTTPException(404,"Node not found")
    if len(network.nodes)<=1: raise HTTPException(400,"At least one node must remain")
    network.nodes.remove(n); log("node.removed",node_id); return {"removed":node_id}
def node_action(node_id,action):
    n=network.get(node_id)
    if not n: raise HTTPException(404,"Node not found")
    if action=="activate" or action=="recover": n.status="active"
    elif action=="deactivate": n.status="idle"
    elif action=="fail": n.status="failed"
    elif action=="validate": return {"node":asdict(n),"validation":chain.validate()}
    log("node.status",f"{node_id} → {n.status}"); return asdict(n)
for action in ["activate","deactivate","validate","fail","recover"]:
    def endpoint(node_id:str,_action=action): return node_action(node_id,_action)
    app.add_api_route(f"/api/nodes/{{node_id}}/{action}",endpoint,methods=["POST"],name=f"node_{action}")
@app.post("/api/network/simulate")
def simulate(body:SimIn): network.latency_ms=body.latency_ms; network.drop_rate=body.drop_rate; log("network.config",f"latency={body.latency_ms}ms drop={body.drop_rate}"); return {"latency_ms":network.latency_ms,"drop_rate":network.drop_rate}
@app.post("/api/network/synchronize")
def synchronize(): network.sync(chain.height); log("network.sync","Active nodes synchronized"); return network.stats()
@app.post("/api/network/reset")
def reset_network():
    global network; network=Network(); network.sync(chain.height); log("network.reset","Network reset to five sample nodes"); return network.stats()
@app.post("/api/security/tamper")
def tamper(body:TamperIn):
    global sandbox
    try: sandbox,result=chain.tamper(body.index)
    except ValueError as e: raise HTTPException(400,str(e))
    log("security.alert",f"Sandbox tamper detected at block {result.get('broken_at')}"); return {"validation":result,"sandbox":[asdict(b) for b in sandbox],"original_preserved":True}
@app.post("/api/security/reset-sandbox")
def reset_sandbox():
    global sandbox; sandbox=None; return {"reset":True,"validation":chain.validate()}
@app.get("/api/activity")
def get_activity(): return activity
@app.get("/api/export")
def export(): return {**chain.export(),"nodes":network.stats()["nodes"],"activity":activity}
@app.get("/api/learning/progress")
def learning_progress(): return {"completed":[]}
@app.post("/api/learning/progress")
def save_learning(body:dict): return {"saved":True,"lesson_id":body.get("lesson_id")}
@app.websocket("/ws")
async def websocket_endpoint(ws:WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        await ws.send_json({"type":"simulation.state","timestamp":time.time(),"payload":stats()})
        while True: await ws.receive_text()
    except WebSocketDisconnect: clients.discard(ws)
