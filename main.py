from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import json, os

app = FastAPI(title="VTX Tiers API")

DATA_FILE  = "tiers.json"
API_SECRET = os.environ.get("API_SECRET", "GANTI_INI_DENGAN_SECRET_KAMU")

# ── helpers ──────────────────────────────────────────────────
def load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def require_secret(x_api_secret: str = Header(...)):
    if x_api_secret != API_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

# ── models ───────────────────────────────────────────────────
class TierEntry(BaseModel):
    minecraft_username: str
    tier:               str   # e.g. "LT5", "HT3", "LT1"
    region:             str   # "AS" or "AU"
    tester:             str

# ── endpoints ────────────────────────────────────────────────
@app.get("/tier/{username}")
def get_tier(username: str):
    data  = load()
    entry = data.get(username.lower())
    if not entry:
        raise HTTPException(status_code=404, detail="Player not found")
    return entry

@app.post("/tier", dependencies=[Depends(require_secret)])
def set_tier(entry: TierEntry):
    data = load()
    data[entry.minecraft_username.lower()] = {
        "minecraft_username": entry.minecraft_username,
        "tier":               entry.tier,
        "region":             entry.region,
        "tester":             entry.tester,
    }
    save(data)
    return {"ok": True, "entry": data[entry.minecraft_username.lower()]}

@app.get("/tiers")
def list_tiers():
    return load()

@app.get("/")
def root():
    return {"status": "VTX Tiers API running"}
