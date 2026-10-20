"""Complap Market uchun SUN'IY (sintetik) noutbuk ma'lumotlari yaratadi.

Diqqat: bu ma'lumotlar real emas, faqat ishlab chiqish va ML modelini sinash uchun.
README da "sun'iy ma'lumot" deb yozing, keyin real narxlar bilan almashtirasiz.

Ishga tushirish:  python generate_data.py
Natija:           laptops_big.csv
"""
import csv
import random

rng = random.Random(42)  # bir xil natija chiqishi uchun
N = 400

# ---------- Do'konlar ----------
DOKONLAR = [
    ("TechZone", "Toshkent"), ("Kompyuter Dunyosi", "Andijon"), ("PC Market", "Samarqand"),
    ("NoutPlus", "Toshkent"), ("Digital House", "Toshkent"), ("LapStore", "Buxoro"),
    ("Texno Olam", "Namangan"), ("ByteShop", "Farg'ona"), ("Gigabayt", "Toshkent"),
    ("Smart Kompyuter", "Qarshi"), ("Chip Market", "Nukus"), ("Core Store", "Xorazm"),
    ("Mega Tech", "Samarqand"), ("IT Bozor", "Toshkent"), ("Pixel Dokon", "Jizzax"),
    ("ProLap", "Navoiy"), ("Texno Savdo", "Andijon"), ("Zamon Kompyuter", "Namangan"),
    ("Orbita PC", "Termiz"), ("Silk Road Tech", "Buxoro"),
]

# ---------- Komponentlar: (nomi, qiymati so'mda) ----------
OFIS_CPU = [
    ("Intel Core i3-1215U", 3.5e6), ("Intel Core i5-1235U", 4.6e6), ("Intel Core i5-1335U", 5.0e6),
    ("Intel Core i7-1255U", 6.2e6), ("Intel Core i7-1355U", 6.8e6),
    ("AMD Ryzen 3 5300U", 3.4e6), ("AMD Ryzen 5 5500U", 4.4e6),
    ("AMD Ryzen 5 7530U", 5.0e6), ("AMD Ryzen 7 7730U", 6.0e6),
]
OFIS_GPU = [("Intel UHD", 0), ("Intel Iris Xe", 0.3e6), ("AMD Radeon Graphics", 0.3e6), ("MX550", 1.2e6)]

GEYMING_CPU = [
    ("Intel Core i5-12450H", 5.0e6), ("Intel Core i5-12500H", 5.4e6), ("Intel Core i5-13420H", 5.6e6),
    ("Intel Core i7-12700H", 7.0e6), ("Intel Core i7-13620H", 7.4e6), ("Intel Core i9-13980HX", 12.0e6),
    ("AMD Ryzen 5 7640HS", 6.0e6), ("AMD Ryzen 7 6800H", 6.6e6),
    ("AMD Ryzen 7 7840HS", 8.0e6), ("AMD Ryzen 9 7945HX", 11.0e6),
]
GEYMING_GPU = [
    ("GTX 1650", 2.2e6), ("RTX 3050", 3.2e6), ("RTX 3050 Ti", 3.8e6), ("RTX 3060", 4.6e6),
    ("RTX 4050", 4.4e6), ("RTX 4060", 5.4e6), ("RTX 4070", 8.5e6), ("RTX 4080", 14.0e6),
]

# Apple: (model nomi, chip, GPU, asosiy narx, RAM variantlari)
APPLE = [
    ("Apple MacBook Air M1", "Apple M1", "Apple M1 GPU", 11.5e6, [8, 16]),
    ("Apple MacBook Air M2", "Apple M2", "Apple M2 GPU", 14.8e6, [8, 16]),
    ("Apple MacBook Air M3", "Apple M3", "Apple M3 GPU", 16.5e6, [8, 16]),
    ("Apple MacBook Pro 14 M3 Pro", "Apple M3 Pro", "Apple M3 Pro GPU", 27.0e6, [18, 36]),
]

RAM_QIYMAT = {8: 0, 16: 0.8e6, 18: 0, 32: 2.2e6, 36: 3.0e6}
SSD_QIYMAT = {256: 0, 512: 0.5e6, 1000: 1.3e6, 2000: 3.0e6}

# (brend + seriya, brend omili)
OFIS_SERIYA = [
    ("Lenovo IdeaPad 3", 1.0), ("Lenovo IdeaPad Slim 5", 1.05), ("Lenovo ThinkPad E14", 1.15),
    ("HP 250 G9", 0.97), ("HP Pavilion 15", 1.02), ("HP ProBook 450", 1.1),
    ("ASUS VivoBook 15", 1.03), ("ASUS Zenbook 14", 1.2), ("Acer Aspire 5", 0.97),
    ("Acer Swift 3", 1.05), ("Dell Inspiron 15", 1.06), ("Dell Latitude 5440", 1.2),
    ("Xiaomi RedmiBook 15", 0.9), ("Xiaomi Mi Notebook Pro", 1.05),
]
GEYMING_SERIYA = [
    ("Lenovo LOQ 15", 1.0), ("Lenovo Legion 5", 1.1), ("ASUS TUF Gaming F15", 1.05),
    ("ASUS ROG Strix G16", 1.2), ("HP Victus 16", 1.0), ("HP Omen 16", 1.12),
    ("Acer Nitro 5", 0.97), ("Acer Predator Helios 16", 1.2), ("MSI Katana 15", 1.05),
    ("MSI Thin GF63", 0.95), ("Dell G15", 1.08), ("Gigabyte G5", 1.0),
]

GLOBAL_OMIL = 0.85  # umumiy narx darajasini sozlash uchun


def yaxlitla(x):
    return int(round(x / 50_000) * 50_000)


def shovqin():
    return rng.uniform(0.93, 1.07)  # do'konlar orasidagi narx farqi


def ofis_noutbuk():
    seriya, brend = rng.choice(OFIS_SERIYA)
    cpu, cpu_q = rng.choice(OFIS_CPU)
    gpu, gpu_q = rng.choices(OFIS_GPU, weights=[3, 5, 3, 1])[0]
    ram = rng.choices([8, 16, 32], weights=[5, 5, 1])[0]
    ssd = rng.choices([256, 512, 1000], weights=[3, 6, 2])[0]
    narx = (2.6e6 + cpu_q + gpu_q + RAM_QIYMAT[ram] + SSD_QIYMAT[ssd]) * brend * GLOBAL_OMIL * shovqin()
    return seriya, yaxlitla(narx), cpu, gpu, ram, ssd


def geyming_noutbuk():
    seriya, brend = rng.choice(GEYMING_SERIYA)
    cpu, cpu_q = rng.choice(GEYMING_CPU)
    gpu, gpu_q = rng.choices(GEYMING_GPU, weights=[2, 5, 3, 4, 4, 5, 2, 1])[0]
    ram = rng.choices([16, 32], weights=[7, 3])[0]
    ssd = rng.choices([512, 1000, 2000], weights=[5, 5, 1])[0]
    narx = (2.0e6 + cpu_q + gpu_q + RAM_QIYMAT[ram] + SSD_QIYMAT[ssd]) * brend * GLOBAL_OMIL * shovqin()
    return seriya, yaxlitla(narx), cpu, gpu, ram, ssd


def apple_noutbuk():
    nom, chip, gpu, asos, ram_variantlar = rng.choice(APPLE)
    ram = rng.choice(ram_variantlar)
    ssd = rng.choices([256, 512, 1000], weights=[3, 5, 2])[0]
    narx = (asos + RAM_QIYMAT[ram] + SSD_QIYMAT[ssd]) * shovqin()
    return nom, yaxlitla(narx), chip, gpu, ram, ssd


def main():
    qatorlar = []
    for _ in range(N):
        tur = rng.choices(["ofis", "geyming", "apple"], weights=[45, 45, 10])[0]
        if tur == "ofis":
            nom, narx, cpu, gpu, ram, ssd = ofis_noutbuk()
        elif tur == "geyming":
            nom, narx, cpu, gpu, ram, ssd = geyming_noutbuk()
        else:
            nom, narx, cpu, gpu, ram, ssd = apple_noutbuk()
        dokon, shahar = rng.choice(DOKONLAR)
        qatorlar.append([dokon, shahar, nom, narx, cpu, gpu, ram, ssd])

    with open("laptops_big.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["shop", "shahar", "nom", "narx", "protsessor", "video_karta", "ram_gb", "ssd_gb"])
        w.writerows(qatorlar)

    print(f"Tayyor: laptops_big.csv ({len(qatorlar)} ta qator)")


if __name__ == "__main__":
    main()
