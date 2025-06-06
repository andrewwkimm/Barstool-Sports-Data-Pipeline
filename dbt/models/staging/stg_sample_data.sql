{{ config(materialized='view') }}

SELECT
    conn_speed,
    gmt_offset,
    event,
    page_title,
    content_duration,
    app_title,
    country_code3,
    region,
    app_os,
    source,
    conn_type,
    country_name,
    latitude,
    as_number,
    content_barstoolBrandID,
    proxy_type,
    content_barstoolContentID,
    content_barstoolTalentID,
    content_type,
    longitude,
    app_version,
    ANONID,
    area_code,
    as_name,
    country_code,
    continent,
    timestamp,
    type,
    postal_code,
    proxy_description,
    metro_code,
    utc_offset,
    city,
    sha1
FROM {{ source('barstool_sports_data', 'sample_data') }}
