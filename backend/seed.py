import json
from pathlib import Path

from config import settings
from database import SessionLocal, init_db
from models import Politician, Promise


def _load_json(name: str):
    path = Path(settings.DATA_DIR) / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def seed_data():
    init_db()
    db = SessionLocal()
    try:
        politicians = _load_json("politicians.json")
        promise_catalog = _load_json("promises.json")

        for key, p_data in politicians.items():
            politician = db.get(Politician, p_data["id"]) or Politician(id=p_data["id"])
            politician.name = p_data["name"]
            politician.title = p_data["title"]
            politician.region = p_data.get("region", "Nasional")
            politician.color = p_data["color"]
            politician.icp_score = p_data["icp"]
            politician.sentinel_status = p_data["sentinel"]
            politician.scores = p_data["scores"]
            db.add(politician)

            promises = promise_catalog.get(key) or p_data.get("promises", [])
            for prom in promises:
                promise_id = prom["id"]
                promise = db.get(Promise, promise_id) or Promise(id=promise_id, politician_id=politician.id)
                promise.politician_id = politician.id
                promise.promise_text = prom.get("promise") or prom.get("promise_text")
                promise.category = prom.get("category")
                promise.status = prom.get("status", "NOT_STARTED")
                promise.analysis = prom.get("analysis")
                db.add(promise)

        db.commit()
        print("Database seeded successfully.")
    except Exception as exc:
        db.rollback()
        print(f"Error seeding database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
