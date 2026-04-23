import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import enum

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_cNbr6p8mPvqH@ep-frosty-rice-aoea3obe.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserTier(str, enum.Enum): STANDARD = "standard"; PREMIUM = "premium"; GOD = "GOD"
class JobStatus(str, enum.Enum): PENDING = "pending"; ASSIGNED = "assigned"; RUNNING = "running"; COMPLETED = "completed"; FAILED = "failed"; CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    tier = Column(String, default="standard")
    balance = Column(Float, default=0)
    earned_total = Column(Float, default=0)
    spent_total = Column(Float, default=0)
    region = Column(String, default="in")
    created_at = Column(DateTime, default=datetime.utcnow)

class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True)
    name = Column(String)
    owner_id = Column(String, index=True)
    gpu_tier = Column(String)
    cpu_cores = Column(Integer, default=4)
    ram_gb = Column(Integer, default=8)
    quality_score = Column(Float, default=1.0)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="online")
    region = Column(String, default="in")
    created_at = Column(DateTime, default=datetime.utcnow)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    type = Column(String)
    status = Column(String, default="pending")
    submitter_id = Column(String, index=True)
    assigned_node_id = Column(String)
    script = Column(Text)
    slices = Column(Integer, default=1)
    credits_cost = Column(Float, default=0)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result_cid = Column(String)
    error = Column(Text)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    type = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sarva API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GPU_MULT = {"rtx-4090": 3.0, "rtx-5090": 3.0, "rtx-3090": 2.5, "rtx-4070": 2.5, "rtx-3060": 2.0, "rtx-2070": 2.0, "gtx-1080": 1.5, "gtx-1080ti": 1.5, "gtx-1660": 1.3, "cpu": 0.8}
GEO_RATE = {"in": 0.7, "india": 0.7, "us": 1.0, "uk": 1.0, "eu": 0.95}
PLATFORM_FEE = 0.20

def qs(g): return GPU_MULT.get(g.lower(), 1.0)
def gr(r): return GEO_RATE.get(r.lower(), 1.0)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/status")
def status():
    db = next(get_db())
    return {"name": "Sarva", "version": "1.0.0", "status": "running", "nodes": db.query(Node).count(), "jobs": db.query(Job).count()}

@app.post("/auth/register")
def register_user(data: dict):
    db = next(get_db())
    if not data.get("user_id") or not data.get("name"): raise HTTPException(400, "user_id and name required")
    user = db.query(User).filter(User.user_id == data["user_id"]).first()
    if not user:
        user = User(user_id=data["user_id"], name=data["name"], region=data.get("region", "in"), tier=UserTier.GOD if data["user_id"] == "god" else UserTier.STANDARD)
        db.add(user); db.commit(); db.refresh(user)
    return {"token": data["user_id"], "user_id": user.user_id, "tier": user.tier, "balance": user.balance}

@app.post("/nodes/register")
def register_node(data: dict):
    db = next(get_db())
    if not data.get("node_name") or not data.get("gpu_tier") or not data.get("owner_id"): raise HTTPException(400, "node_name, gpu_tier, owner_id required")
    import uuid
    node_id = str(uuid.uuid4())[:12]
    node = Node(node_id=node_id, name=data["node_name"], owner_id=data["owner_id"], gpu_tier=data["gpu_tier"], cpu_cores=data.get("cpu_cores", 4), ram_gb=data.get("ram_gb", 8), quality_score=qs(data["gpu_tier"]), region=data.get("region", "in"))
    db.add(node); db.commit()
    return {"node_id": node_id, "quality_score": node.quality_score, "message": "Node registered"}

@app.post("/nodes/heartbeat")
def node_heartbeat(data: dict):
    db = next(get_db())
    node = db.query(Node).filter(Node.node_id == data["node_id"]).first()
    if not node: raise HTTPException(404, "Node not found")
    node.last_heartbeat = datetime.utcnow()
    if data.get("status"): node.status = data["status"]
    db.commit()
    return {"ok": True, "time": node.last_heartbeat}

@app.get("/nodes")
def list_nodes():
    db = next(get_db())
    cutoff = datetime.utcnow().timestamp() - 90
    nodes = db.query(Node).all()
    return {"nodes": [{"id": n.node_id, "name": n.name, "owner_id": n.owner_id, "gpu_tier": n.gpu_tier, "cpu_cores": n.cpu_cores, "ram_gb": n.ram_gb, "quality_score": n.quality_score, "status": n.status, "region": n.region, "online": n.last_heartbeat.timestamp() > cutoff} for n in nodes], "count": len(nodes)}

@app.post("/jobs/submit")
def submit_job(data: dict):
    db = next(get_db())
    if not data.get("type") or not data.get("submitter_id"): raise HTTPException(400, "type and submitter_id required")
    user = db.query(User).filter(User.user_id == data["submitter_id"]).first()
    if not user: user = User(user_id=data["submitter_id"], tier=UserTier.GOD if data["submitter_id"] == "god" else UserTier.STANDARD); db.add(user); db.commit(); db.refresh(user)
    n = data.get("slices", 1)
    gpu_cost = 2.5 if data["type"] == "ml" else 3.0 if data["type"] == "gaming" else 1.0
    cost = n * gpu_cost * gr(user.region)
    final_cost = 0 if user.tier == UserTier.GOD else cost
    if user.tier != UserTier.GOD and user.balance < final_cost: raise HTTPException(400, f"Insufficient credits. Required: {final_cost}, Balance: {user.balance}")
    import uuid
    job_id = str(uuid.uuid4())[:12]
    job = Job(job_id=job_id, type=data["type"], submitter_id=data["submitter_id"], script=data.get("script"), slices=n, credits_cost=final_cost, priority=data.get("priority", 0))
    if user.tier != UserTier.GOD: user.balance -= final_cost; user.spent_total += final_cost
    db.add(job); db.commit()
    return {"job_id": job_id, "status": "pending", "estimated_cost": final_cost}

@app.post("/jobs/{job_id}/complete")
def complete_job(job_id: str, data: dict):
    db = next(get_db())
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job: raise HTTPException(404, "Job not found")
    job.status = "failed" if data.get("error") else "completed"
    job.completed_at = datetime.utcnow()
    job.result_cid = data.get("result_cid")
    job.error = data.get("error")
    if job.assigned_node_id and not data.get("error") and job.credits_cost > 0:
        node = db.query(Node).filter(Node.node_id == job.assigned_node_id).first()
        if node:
            node.status = "online"
            earn_mult = qs(node.gpu_tier) * gr(node.region)
            earned = job.credits_cost * earn_mult * (1 - PLATFORM_FEE)
            owner = db.query(User).filter(User.user_id == node.owner_id).first()
            if owner: owner.balance += earned; owner.earned_total += earned
    db.commit()
    return {"ok": True}

@app.get("/jobs")
def list_jobs(status: str = None, submitter_id: str = None):
    db = next(get_db())
    q = db.query(Job)
    if status: q = q.filter(Job.status == status)
    if submitter_id: q = q.filter(Job.submitter_id == submitter_id)
    jobs = q.order_by(Job.created_at.desc()).all()
    return {"jobs": [{"id": j.job_id, "type": j.type, "status": j.status, "submitter_id": j.submitter_id, "assigned_node_id": j.assigned_node_id, "credits_cost": j.credits_cost, "created_at": j.created_at.isoformat() if j.created_at else None} for j in jobs], "count": len(jobs)}

@app.get("/jobs/next")
def next_job(node_id: str = Query(...)):
    db = next(get_db())
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node: raise HTTPException(404, "Node not found")
    job = db.query(Job).filter(Job.status == "pending").order_by(Job.priority.desc(), Job.created_at.asc()).first()
    if not job: return {"job": None}
    job.status = "assigned"; job.assigned_node_id = node_id; job.updated_at = datetime.utcnow(); node.status = "busy"
    db.commit()
    return {"job": {"id": job.job_id, "type": job.type, "script": job.script, "slices": job.slices}}

@app.get("/credits/{user_id}")
def get_credits(user_id: str):
    db = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    return {"user_id": user.user_id, "balance": user.balance, "tier": user.tier, "earned_total": user.earned_total, "spent_total": user.spent_total}

@app.get("/credits/leaderboard")
def leaderboard():
    db = next(get_db())
    users = db.query(User).filter(User.tier != UserTier.GOD).order_by(User.earned_total.desc()).limit(20).all()
    return {"leaderboard": [{"user_id": u.user_id, "earned_total": round(u.earned_total, 2)} for u in users]}

@app.post("/credits/cashout")
def cashout(data: dict):
    db = next(get_db())
    user = db.query(User).filter(User.user_id == data["user_id"]).first()
    if not user: raise HTTPException(404, "User not found")
    amount = float(data["amount"])
    if user.balance < 500: raise HTTPException(400, f"Minimum cashout Rs.500. Balance: {user.balance}")
    if user.balance < amount: raise HTTPException(400, "Insufficient balance")
    user.balance -= amount
    tx = Transaction(user_id=user.user_id, type="cashout", amount=-amount)
    db.add(tx); db.commit()
    return {"ok": True, "message": f"Cashout Rs.{amount} requested. 24-48hrs."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)