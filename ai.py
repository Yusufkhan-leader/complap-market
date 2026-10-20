"""AI qismi: narx bashorati va "arzon / adolatli / qimmat" bahosi.

Avval  python train_model.py  ni ishga tushirib, price_model.joblib ni yarating.
"""
import os

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler

from db import get_connection

router = APIRouter(prefix="/ai", tags=["AI"])

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "price_model.joblib")
model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

FEATURES = ["brend", "protsessor", "video_karta", "ram_gb", "ssd_gb"]
CHEGARA = 0.10  # bashoratdan 10% dan ko'p farq qilsa "arzon" yoki "qimmat"


class SpecsIn(BaseModel):
    brend: str
    protsessor: str
    video_karta: str
    ram_gb: int
    ssd_gb: int


def baho_ber(narx: float, bashorat: float) -> str:
    farq = (narx - bashorat) / bashorat
    if farq < -CHEGARA:
        return "arzon"
    if farq > CHEGARA:
        return "qimmat"
    return "adolatli"


def add_price_labels(rows: list) -> list:
    """Mahsulotlar ro'yxatiga bashorat narx va baho qo'shadi (model bo'lsa)."""
    if model is None or not rows:
        return rows

    df = pd.DataFrame(
        {
            "brend": [r["nom"].split()[0] for r in rows],
            "protsessor": [r["protsessor"] for r in rows],
            "video_karta": [r["video_karta"] for r in rows],
            "ram_gb": [r["ram_gb"] for r in rows],
            "ssd_gb": [r["ssd_gb"] for r in rows],
        }
    )
    bashoratlar = model.predict(df[FEATURES])

    for r, b in zip(rows, bashoratlar):
        b = max(float(b), 1.0)
        r["bashorat_narx"] = int(round(b, -4))
        r["farq_foiz"] = round((float(r["narx"]) - b) / b * 100, 1)
        r["baho"] = baho_ber(float(r["narx"]), b)
    return rows


@router.post("/predict-price")
def predict_price(data: SpecsIn):
    if model is None:
        raise HTTPException(status_code=503, detail="Model topilmadi. train_model.py ni ishga tushiring.")
    df = pd.DataFrame([data.model_dump()])
    narx = float(model.predict(df[FEATURES])[0])
    return {"bashorat_narx": int(round(narx, -4))}


@router.get("/price-check/{product_id}")
def price_check(product_id: int):
    if model is None:
        raise HTTPException(status_code=503, detail="Model topilmadi. train_model.py ni ishga tushiring.")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.nom, p.narx, s.protsessor, s.video_karta, s.ram_gb, s.ssd_gb
                FROM products p JOIN specs s ON s.product_id = p.id
                WHERE p.id = %s
                """,
                (product_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return add_price_labels([row])[0]


# ---------- O'xshash mahsulotlar tavsiyasi ----------
# Qaysi xususiyat o'xshashlikda qanchalik muhim (katta son = muhimroq)
AGIRLIK = {
    "video_karta": 2.0,
    "protsessor": 1.5,
    "brend": 0.7,
    "narx_log": 2.0,
    "ram_gb": 1.0,
    "ssd_gb": 0.6,
}


def oxshashlarni_top(rows: list, product_id: int, limit: int = 4):
    """Berilgan mahsulotga eng o'xshash `limit` ta mahsulotni topadi."""
    df = pd.DataFrame(rows)
    if df.empty or product_id not in set(df["id"]):
        return None

    df["brend"] = df["nom"].str.split().str[0]
    df["narx_log"] = np.log(df["narx"].astype(float))

    # Kategorik ustunlar: one-hot kodlash, og'irlikka ko'paytiriladi
    bloklar = []
    for ustun in ["video_karta", "protsessor", "brend"]:
        bloklar.append(pd.get_dummies(df[ustun]).astype(float).values * AGIRLIK[ustun])

    # Sonli ustunlar: 0..1 oralig'iga keltiriladi, og'irlikka ko'paytiriladi
    sonli_ustunlar = ["narx_log", "ram_gb", "ssd_gb"]
    sonli = MinMaxScaler().fit_transform(df[sonli_ustunlar].astype(float))
    sonli = sonli * np.array([AGIRLIK[u] for u in sonli_ustunlar])
    bloklar.append(sonli)

    X = np.hstack(bloklar)
    pozitsiya = int(np.where(df["id"].values == product_id)[0][0])
    masofa = euclidean_distances(X[pozitsiya : pozitsiya + 1], X)[0]
    masofa[pozitsiya] = np.inf  # o'zini ro'yxatga qo'shmaymiz

    natija = []
    for i in np.argsort(masofa)[:limit]:
        r = df.iloc[int(i)]
        natija.append(
            {
                "id": int(r["id"]),
                "nom": r["nom"],
                "narx": int(r["narx"]),
                "protsessor": r["protsessor"],
                "video_karta": r["video_karta"],
                "ram_gb": int(r["ram_gb"]),
                "ssd_gb": int(r["ssd_gb"]),
                "dokon": r["dokon"],
                "shahar": r["shahar"],
                "oxshashlik": int(round(100 * np.exp(-masofa[i] / 3))),
            }
        )
    return natija


@router.get("/similar/{product_id}")
def similar(product_id: int, limit: int = 4):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.nom, p.narx, s.protsessor, s.video_karta, s.ram_gb, s.ssd_gb,
                       sh.nom AS dokon, sh.shahar
                FROM products p
                JOIN specs s  ON s.product_id = p.id
                JOIN shops sh ON sh.id = p.shop_id
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    natija = oxshashlarni_top(rows, product_id, max(1, min(limit, 12)))
    if natija is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return natija
