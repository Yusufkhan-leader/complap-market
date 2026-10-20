"""Do'kon egalari uchun: ro'yxatdan o'tish, kirish, mahsulot qo'shish.

O'rnatish:  pip install bcrypt PyJWT
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg2.errors import UniqueViolation
from pydantic import BaseModel

from db import get_connection

router = APIRouter(prefix="/seller", tags=["Do'kon egalari"])

SECRET_KEY = os.getenv("SECRET_KEY")  # .env faylidan olinadi
if not SECRET_KEY:
    raise RuntimeError(".env faylida SECRET_KEY topilmadi. .env.example ga qarang.")
ALGORITHM = "HS256"
security = HTTPBearer()


# ---------- Ma'lumot shakllari ----------
class RegisterIn(BaseModel):
    nom: str
    shahar: str
    telefon: str
    email: str
    parol: str


class LoginIn(BaseModel):
    email: str
    parol: str


class ProductIn(BaseModel):
    nom: str
    narx: int
    protsessor: str
    video_karta: str
    ram_gb: int
    ssd_gb: int
    rasm_url: Optional[str] = None


# ---------- Yordamchi funksiyalar ----------
def create_token(shop_id: int) -> str:
    payload = {
        "shop_id": shop_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_shop(creds: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["shop_id"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token yaroqsiz yoki muddati tugagan")


# ---------- Endpointlar ----------
@router.post("/register")
def register(data: RegisterIn):
    if len(data.parol) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgi bo'lsin")

    parol_hash = bcrypt.hashpw(data.parol.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO shops (nom, shahar, telefon, email, parol_hash) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (data.nom, data.shahar, data.telefon, data.email, parol_hash),
            )
            shop_id = cur.fetchone()["id"]
        conn.commit()
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Bu do'kon nomi yoki email band")
    finally:
        conn.close()

    return {"message": "Ro'yxatdan o'tdingiz", "shop_id": shop_id}


@router.post("/login")
def login(data: LoginIn):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, parol_hash FROM shops WHERE email = %s", (data.email,)
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None or not row["parol_hash"] or not bcrypt.checkpw(
        data.parol.encode(), row["parol_hash"].encode()
    ):
        raise HTTPException(status_code=401, detail="Email yoki parol noto'g'ri")

    return {"access_token": create_token(row["id"]), "token_type": "bearer"}


@router.post("/products")
def add_product(data: ProductIn, shop_id: int = Depends(get_current_shop)):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (shop_id, nom, narx, rasm_url) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (shop_id, data.nom, data.narx, data.rasm_url),
            )
            product_id = cur.fetchone()["id"]
            cur.execute(
                "INSERT INTO specs (product_id, protsessor, video_karta, ram_gb, ssd_gb) "
                "VALUES (%s, %s, %s, %s, %s)",
                (product_id, data.protsessor, data.video_karta, data.ram_gb, data.ssd_gb),
            )
        conn.commit()
    finally:
        conn.close()

    return {"message": "Mahsulot qo'shildi", "product_id": product_id}
