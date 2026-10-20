"""Complap Market: noutbuk narxini bashorat qiluvchi model.

O'rnatish:  pip install pandas scikit-learn joblib
Ishga tushirish:  python train_model.py
Natija:           price_model.joblib (saqlangan model)
"""
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from db import get_connection

KATEGORIK = ["brend", "protsessor", "video_karta"]
SONLI = ["ram_gb", "ssd_gb"]


def malumot_yuklash() -> pd.DataFrame:
    """Bazadan mahsulotlarni DataFrame ko'rinishida oladi."""
    sql = """
        SELECT p.nom, p.narx, s.protsessor, s.video_karta, s.ram_gb, s.ssd_gb
        FROM products p
        JOIN specs s ON s.product_id = p.id
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            qatorlar = cur.fetchall()
    finally:
        conn.close()
    return pd.DataFrame(qatorlar)


def tayyorlash(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["narx"] = df["narx"].astype(float)
    # Brend: nomning birinchi so'zi (Lenovo, ASUS, HP, Apple...)
    df["brend"] = df["nom"].str.split().str[0]
    return df.dropna(subset=KATEGORIK + SONLI + ["narx"])


def model_yaratish(regressor) -> Pipeline:
    qayta_ishlash = ColumnTransformer(
        [
            ("kategorik", OneHotEncoder(handle_unknown="ignore"), KATEGORIK),
            ("sonli", "passthrough", SONLI),
        ]
    )
    return Pipeline([("prep", qayta_ishlash), ("model", regressor)])


def main():
    df = tayyorlash(malumot_yuklash())
    print(f"Ma'lumotlar soni: {len(df)}")
    print(df["narx"].describe().round(0).to_string(), "\n")

    X = df[KATEGORIK + SONLI]
    y = df["narx"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    nomzodlar = {
        "Oddiy o'rtacha (baseline)": DummyRegressor(strategy="mean"),
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=300, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }

    natijalar = {}
    for nom, regressor in nomzodlar.items():
        model = model_yaratish(regressor)
        model.fit(X_train, y_train)
        taxmin = model.predict(X_test)
        mae = mean_absolute_error(y_test, taxmin)
        r2 = r2_score(y_test, taxmin)
        natijalar[nom] = (mae, r2)
        print(f"{nom:28s} MAE: {mae:>12,.0f} so'm   R2: {r2:.3f}")

    eng_yaxshi = min(
        (n for n in natijalar if "baseline" not in n), key=lambda n: natijalar[n][0]
    )
    print(f"\nEng yaxshi model: {eng_yaxshi}")

    # Eng yaxshi modelni barcha ma'lumotda qayta o'rgatib saqlaymiz
    yakuniy = model_yaratish(nomzodlar[eng_yaxshi])
    yakuniy.fit(X, y)
    joblib.dump(yakuniy, "price_model.joblib")
    print("Model saqlandi: price_model.joblib")

    # Namuna bashorat
    namuna = pd.DataFrame(
        [
            {
                "brend": "Lenovo",
                "protsessor": "Intel Core i5-12450H",
                "video_karta": "RTX 3050",
                "ram_gb": 16,
                "ssd_gb": 512,
            }
        ]
    )
    print(f"\nNamuna: Lenovo, i5-12450H, RTX 3050, 16GB, 512GB SSD")
    print(f"Bashorat qilingan narx: {yakuniy.predict(namuna)[0]:,.0f} so'm")


if __name__ == "__main__":
    main()
