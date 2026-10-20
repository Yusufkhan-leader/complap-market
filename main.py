"""Complap Market API.

Ishga tushirish:  python -m uvicorn main:app --reload
Hujjat:           http://127.0.0.1:8000/docs
"""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ai import add_price_labels, router as ai_router
from db import get_connection
from seller import router as seller_router

app = FastAPI(title="Complap Market")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Do'kon egalari bo'limi (ro'yxatdan o'tish, kirish, mahsulot qo'shish)
app.include_router(seller_router)

# AI bo'limi (narx bashorati va baho)
app.include_router(ai_router)


@app.get("/")
def root():
    return {"message": "Complap Market API ishlayapti"}


@app.get("/products")
def get_products(
    q: Optional[str] = None,            # nom bo'yicha qidiruv
    protsessor: Optional[str] = None,   # masalan: i5, Ryzen
    video_karta: Optional[str] = None,  # masalan: RTX 4060
    min_narx: Optional[int] = None,
    max_narx: Optional[int] = None,
):
    sql = """
        SELECT p.id, p.nom, p.narx, p.rasm_url,
               s.protsessor, s.video_karta, s.ram_gb, s.ssd_gb,
               sh.nom AS dokon, sh.shahar
        FROM products p
        JOIN specs s  ON s.product_id = p.id
        JOIN shops sh ON sh.id = p.shop_id
        WHERE 1=1
    """
    params = []

    if q:
        sql += " AND p.nom ILIKE %s"
        params.append(f"%{q}%")
    if protsessor:
        sql += " AND s.protsessor ILIKE %s"
        params.append(f"%{protsessor}%")
    if video_karta:
        sql += " AND s.video_karta ILIKE %s"
        params.append(f"%{video_karta}%")
    if min_narx is not None:
        sql += " AND p.narx >= %s"
        params.append(min_narx)
    if max_narx is not None:
        sql += " AND p.narx <= %s"
        params.append(max_narx)

    sql += " ORDER BY p.narx"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    # Har bir mahsulotga AI bashorat narxi va bahosi qo'shiladi
    return add_price_labels(rows)


@app.get("/products/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.nom, p.narx, p.rasm_url,
                       s.protsessor, s.video_karta, s.ram_gb, s.ssd_gb,
                       sh.nom AS dokon, sh.shahar, sh.telefon
                FROM products p
                JOIN specs s  ON s.product_id = p.id
                JOIN shops sh ON sh.id = p.shop_id
                WHERE p.id = %s
                """,
                (product_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return row
