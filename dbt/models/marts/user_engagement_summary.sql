{{ config(materialized='table') }}

WITH events AS (
    SELECT
        content_barstoolContentID AS content_id,
        content_barstoolTalentID AS talent_id,
        proxy_description,
        content_type,
        country_name,
        city,
        timestamp,
        event,
        content_duration::FLOAT64 AS duration_seconds
    FROM {{ ref('stg_sample_data') }}
    WHERE event IS NOT NULL
),

content AS (
    SELECT
        SHARE_URL AS content_id,
        TITLE,
        TYPE AS content_type_csv,
        TALENT AS talent_name,
        FRANCHISE
    FROM {{ ref('stg_prod_content') }}
),

talent AS (
    SELECT
        _ID AS talent_id,
        NAME,
        TYPE AS talent_type
    FROM {{ ref('stg_brands_talent') }}
)

SELECT
    e.content_id,
    c.TITLE,
    c.content_type_csv,
    e.content_type,
    t.NAME AS talent_name,
    t.talent_type,
    e.country_name,
    e.city,
    COUNT(*) AS views,
    AVG(e.duration_seconds) AS avg_duration_seconds,
    MIN(e.timestamp) AS first_seen,
    MAX(e.timestamp) AS last_seen
FROM events e
LEFT JOIN content c ON e.content_id = c.content_id
LEFT JOIN talent t ON e.talent_id = t.talent_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
