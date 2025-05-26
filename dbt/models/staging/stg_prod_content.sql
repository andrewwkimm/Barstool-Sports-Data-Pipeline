{{ config(materialized='view') }}

SELECT
    TITLE,
    TYPE,
    SHARE_URL,
    TAGS,
    TALENT,
    FRANCHISE,
    PUBLISHED_AT
FROM {{ source('barstool_sports_data', 'prod_contents') }}
