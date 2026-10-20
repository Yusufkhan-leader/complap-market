# Complap Market

**computers & laptops**: O'zbekiston bo'ylab noutbuk va kompyuter do'konlarini bir joyga yig'adigan marketplace ilovasi, AI yordamida narx bahosi va o'xshash mahsulot tavsiyasi bilan.

> Bu o'quv/portfolio loyihasi. Ma'lumotlar bazasidagi mahsulotlar va narxlar **sun'iy (sintetik) yaratilgan**, real bozor narxlari emas.

## Muammo va g'oya

Noutbuk tanlayotgan odam turli do'konlarni birma-bir aylanib chiqishga majbur. Complap Market:

- **Xaridorga:** noutbukni nomi bo'yicha qidirish, protsessor, video karta, RAM va narx bo'yicha filtrlash imkonini beradi.
- **Do'kon egasiga:** ro'yxatdan o'tib, o'z mahsulotlarini rasm, xususiyat va narx bilan joylashtirish imkonini beradi.
- **AI orqali:** narx adolatlimi (arzon / adolatli / qimmat) va qanday o'xshash variantlar bor, shuni ko'rsatadi.

## Imkoniyatlar

- Qidiruv va filtr (nom, protsessor, video karta, narx oralig'i)
- Do'kon egalari uchun ro'yxatdan o'tish va kirish (JWT, parollar `bcrypt` bilan shifrlangan)
- Do'kon paneli orqali yangi mahsulot qo'shish
- **Narx bashorati:** ML modeli xususiyatlarga qarab adolatli narxni topadi, kartada "Arzon / Adolatli narx / Qimmat" belgisi chiqadi
- **O'xshash mahsulotlar:** har bir noutbuk uchun xususiyat va narx bo'yicha eng yaqin variantlar

## Texnologiyalar

| Qism | Texnologiya |
|------|-------------|
| Backend | Python, FastAPI |
| Ma'lumotlar bazasi | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| ML / Data Science | pandas, NumPy, scikit-learn |
| Xavfsizlik | JWT, bcrypt, `.env` sozlamalari |

## Loyiha tuzilishi

```
complap-market/
├── main.py            # FastAPI ilovasi, mahsulot endpointlari
├── seller.py          # do'kon egalari: ro'yxat, kirish, mahsulot qo'shish
├── ai.py              # AI endpointlari: narx bahosi, o'xshash mahsulotlar
├── db.py              # bazaga ulanish
├── train_model.py     # narx modelini o'rgatish
├── generate_data.py   # sun'iy ma'lumot yaratish
├── load_data.py       # CSV ni bazaga yuklash
├── schema.sql         # jadvallar
├── migration.sql      # shops jadvaliga login ustunlari
├── index.html         # xaridor sahifasi
└── seller.html        # do'kon paneli
```

## Ishga tushirish

1. **Repozitoriyani yuklab oling va kutubxonalarni o'rnating**
   ```bash
   pip install -r requirements.txt
   ```
2. **PostgreSQL'da baza yarating** (`laptop_market`), so'ng `schema.sql` va `migration.sql` ni ketma-ket ishga tushiring.
3. **Sozlamalar:** `.env.example` ni `.env` nomiga nusxalab, baza paroli va `SECRET_KEY` ni yozing.
4. **Ma'lumot yarating va yuklang**
   ```bash
   python generate_data.py
   python load_data.py laptops_big.csv
   ```
5. **Modelni o'rgating**
   ```bash
   python train_model.py
   ```
6. **Serverni ishga tushiring**
   ```bash
   python -m uvicorn main:app --reload
   ```
7. `index.html` (xaridor) va `seller.html` (do'kon paneli) fayllarini brauzerda oching. API hujjati: http://127.0.0.1:8000/docs

## AI qismi qanday ishlaydi

### Narx bashorati
- Xususiyatlar: brend (nomdan ajratilgan), protsessor, video karta, RAM, SSD.
- Kategorik ustunlar `OneHotEncoder` bilan kodlanadi.
- Solishtirilgan modellar: oddiy o'rtacha (baseline), Linear Regression, Random Forest, Gradient Boosting.
- Sun'iy ma'lumotda eng yaxshi natija: **Linear Regression, MAE ≈ 0,9 mln so'm (baseline: ≈ 4,2 mln), R² ≈ 0,92**.
- **Eslatma:** ma'lumot komponent narxlarining yig'indisi asosida yaratilgani uchun chiziqli model yaxshi ishlaydi. Real bozor narxlarida xato kattaroq bo'lishi va murakkabroq modellar foydali chiqishi kutiladi.
- Mahsulot narxi bashoratdan 10% dan ko'p past bo'lsa "arzon", 10% dan ko'p yuqori bo'lsa "qimmat" deb belgilanadi.

### O'xshash mahsulotlar
- Kategorik xususiyatlar (video karta, protsessor, brend) one-hot, sonlilar (narx, RAM, SSD) 0 dan 1 gacha normallashtirilgan vektorga aylantiriladi.
- Xususiyatlarga og'irlik beriladi (video karta va narx eng muhim).
- Eng yaqin vektorlar **Euclidean masofa** bo'yicha topiladi. Narx va RAM kabi sonli xususiyatlar uchun cosine similarity o'rniga masofa to'g'riroq natija bergani uchun shu tanlandi.

## Kelgusi rejalar

- Real do'kon narxlari bilan ma'lumotni almashtirish va modelni qayta baholash
- Oddiy tilda aqlli qidiruv ("o'yin uchun 8 mln gacha noutbuk")
- Rasm yuklash, kompyuter komplektlari va aksessuarlar bo'limi
- Frontendni React'ga ko'chirish, deploy qilish

## Muallif

Muhammadyusuf · AI / Data Science yo'nalishi
