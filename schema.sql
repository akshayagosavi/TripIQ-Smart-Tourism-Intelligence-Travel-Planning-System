-- =============================================================
--  Smart Tourism Analytics — schema.sql
--  Database: smart_tourism
--  Run: psql -U postgres -d smart_tourism -f schema.sql
-- =============================================================

-- Drop tables if they exist (clean slate)
DROP TABLE IF EXISTS fact_reviews CASCADE;
DROP TABLE IF EXISTS fact_visits CASCADE;
DROP TABLE IF EXISTS dim_hotels CASCADE;
DROP TABLE IF EXISTS dim_destination CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;

-- =============================================================
-- DIMENSION TABLES
-- =============================================================

CREATE TABLE dim_time (
    time_id         VARCHAR(10) PRIMARY KEY,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    season          VARCHAR(10) NOT NULL,
    is_peak_travel  SMALLINT DEFAULT 0
);

CREATE TABLE dim_destination (
    destination_id      VARCHAR(20) PRIMARY KEY,
    country             VARCHAR(100),
    iso_code            VARCHAR(10),
    continent           VARCHAR(50),
    destination_type    VARCHAR(20),
    city                VARCHAR(100),
    state               VARCHAR(100),
    hotel_country       VARCHAR(100)
);

CREATE TABLE dim_hotels (
    offering_id     BIGINT PRIMARY KEY,
    hotel_name      VARCHAR(255),
    hotel_class     FLOAT,
    region_id       BIGINT,
    type            VARCHAR(50),
    city            VARCHAR(100),
    state           VARCHAR(100),
    hotel_country   VARCHAR(100),
    street          VARCHAR(255),
    details         TEXT
);

-- =============================================================
-- FACT TABLES
-- =============================================================

CREATE TABLE fact_visits (
    id              SERIAL PRIMARY KEY,
    country         VARCHAR(100) NOT NULL,
    iso_code        VARCHAR(10),
    year            INTEGER NOT NULL,
    arrivals        FLOAT,
    data_status     VARCHAR(20),
    continent       VARCHAR(50)
);

CREATE TABLE fact_reviews (
    review_id           BIGINT PRIMARY KEY,
    hotel_id            BIGINT REFERENCES dim_hotels(offering_id) ON DELETE SET NULL,
    title               TEXT,
    text                TEXT,
    date_stayed         DATE,
    num_helpful_votes   INTEGER,
    date                DATE,
    via_mobile          BOOLEAN,
    review_year         INTEGER,
    review_month        INTEGER,
    review_quarter      INTEGER,
    rating_overall      FLOAT,
    rating_service      FLOAT,
    rating_cleanliness  FLOAT,
    rating_value        FLOAT,
    rating_location     FLOAT,
    rating_sleep        FLOAT,
    rating_rooms        FLOAT
);

-- =============================================================
-- INDEXES (for faster queries in Power BI / Streamlit)
-- =============================================================

CREATE INDEX idx_fact_visits_country   ON fact_visits(country);
CREATE INDEX idx_fact_visits_year      ON fact_visits(year);
CREATE INDEX idx_fact_visits_continent ON fact_visits(continent);

CREATE INDEX idx_fact_reviews_hotel    ON fact_reviews(hotel_id);
CREATE INDEX idx_fact_reviews_year     ON fact_reviews(review_year);
CREATE INDEX idx_fact_reviews_rating   ON fact_reviews(rating_overall);

CREATE INDEX idx_dim_hotels_city       ON dim_hotels(city);
CREATE INDEX idx_dim_hotels_class      ON dim_hotels(hotel_class);

-- =============================================================
-- VERIFY
-- =============================================================
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
