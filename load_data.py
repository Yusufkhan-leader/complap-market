"""CSV dagi noutbuklarni PostgreSQL bazasiga yuklaydi.

Ishga tushirish:
    python load_data.py laptops_big.csv
Fayl nomi berilmasa, laptops.csv o'qiladi.
"""
import csv
import sys

from db import get_connection

fayl = sys.argv[1] if len(sys.argv) > 1 else "laptops.csv"

conn = get_connection()
cur = conn.cursor()

soni = 0
with open(fayl, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        # 1. Do'kon (bo'lmasa qo'shiladi)
        cur.execute(
            "INSERT INTO shops (nom, shahar) VALUES (%s, %s) "
            "ON CONFLICT (nom) DO NOTHING",
            (row["shop"], row["shahar"]),
        )
        cur.execute("SELECT id FROM shops WHERE nom = %s", (row["shop"],))
        shop_id = cur.fetchone()["id"]

        # 2. Mahsulot
        cur.execute(
            "INSERT INTO products (shop_id, nom, narx) VALUES (%s, %s, %s) RETURNING id",
            (shop_id, row["nom"], int(row["narx"])),
        )
        product_id = cur.fetchone()["id"]

        # 3. Xususiyatlar
        cur.execute(
            "INSERT INTO specs (product_id, protsessor, video_karta, ram_gb, ssd_gb) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                product_id,
                row["protsessor"],
                row["video_karta"],
                int(row["ram_gb"]),
                int(row["ssd_gb"]),
            ),
        )
        soni += 1

conn.commit()
cur.close()
conn.close()
print(f"Tayyor! {soni} ta mahsulot yuklandi.")
