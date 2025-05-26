{{ config(materialized='view') }}

SELECT
    _ID,
    NAME,
    SHORT_NAME,
    TYPE
FROM {{ source('barstool_sports_data', 'brands_talent_franchise') }}
