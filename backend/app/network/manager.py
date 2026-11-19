from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid, random
@dataclass
class Node:
    id: str
    type: str="full"
    status: str="active"
    ip: str="127.0.0.1"
    height: int=0
    peers: int=0
    last_sync: str="just now"
class Network:
    def __init__(self):
        self.nodes=[Node("node-01","full","active","10.0.0.1"),Node("miner-01","miner","active","10.0.0.2"),Node("validator-01","validator","active","10.0.0.3"),Node("node-04","full","idle","10.0.0.4"),Node("node-05","validator","active","10.0.0.5")]
        self.latency_ms=40; self.drop_rate=0.0
    def add(self, kind="full"):
        n=Node(f"{kind}-{uuid.uuid4().hex[:5]}",kind,"active",f"10.0.0.{random.randint(10,240)}"); self.nodes.append(n); return n
    def get(self, node_id):
        return next((n for n in self.nodes if n.id==node_id),None)
    def sync(self,height):
        for n in self.nodes:
            if n.status=="active": n.height=height; n.last_sync=datetime.now(timezone.utc).isoformat()
    def stats(self):
        return {"total_nodes":len(self.nodes),"active_nodes":sum(n.status=="active" for n in self.nodes),"idle_nodes":sum(n.status=="idle" for n in self.nodes),"failed_nodes":sum(n.status=="failed" for n in self.nodes),"nodes":[asdict(n) for n in self.nodes]}
