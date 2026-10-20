-- Bazani yaratish: psql da  CREATE DATABASE laptop_market;  keyin shu faylni ishga tushiring

CREATE TABLE shops (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL UNIQUE,
    shahar      VARCHAR(50),
    telefon     VARCHAR(20),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    shop_id     INT NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    nom         VARCHAR(200) NOT NULL,
    narx        BIGINT NOT NULL,          -- so'mda
    rasm_url    TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE specs (
    product_id   INT PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    protsessor   VARCHAR(100),
    video_karta  VARCHAR(100),
    ram_gb       INT,
    ssd_gb       INT
);

-- Filtr tezroq ishlashi uchun
CREATE INDEX idx_products_narx ON products(narx);
CREATE INDEX idx_specs_protsessor ON specs(protsessor);
CREATE INDEX idx_specs_video_karta ON specs(video_karta);
