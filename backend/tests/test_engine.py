from app.blockchain.engine import Blockchain, Block, canonical

def test_hash_deterministic():
    b=Block(1,1.0,[],"a",0,"",1,"m"); assert b.calculate_hash()==b.calculate_hash()
def test_genesis_and_link():
    c=Blockchain(1); assert c.height==0 and c.validate()["valid"]
def test_pow_and_transaction():
    c=Blockchain(1); c.add_transaction("alice","bob",12,"test"); b,attempts,_=c.mine_pending("miner-01",1)
    assert attempts>0 and b.hash.startswith("0") and c.validate()["valid"] and c.balance("alice")==988
def test_pending_double_spend_prevented():
    c=Blockchain(); c.add_transaction("alice","bob",900)
    try: c.add_transaction("alice","carol",200)
    except ValueError as e: assert "Insufficient" in str(e)
    else: assert False
def test_tamper_sandbox_cascade():
    c=Blockchain(1); c.add_transaction("alice","bob",1); c.mine_pending(difficulty=1)
    sandbox,result=c.tamper(1); assert not result["valid"] and result["broken_at"]==1 and c.validate()["valid"]
