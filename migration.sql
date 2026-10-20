-- pgAdmin da laptop_market bazasida Query Tool orqali ishga tushiring
ALTER TABLE shops
    ADD COLUMN email VARCHAR(100) UNIQUE,
    ADD COLUMN parol_hash TEXT;
