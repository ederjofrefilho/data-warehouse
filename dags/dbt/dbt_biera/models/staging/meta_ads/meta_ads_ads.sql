WITH source AS (
    SELECT
        ads.id,
        ads.adset_id,
        ads.created_time,
        ads.effective_status,
        ads.updated_time,
        creatives.image_url AS creative_url_image,
        creatives.instagram_permalink_url AS Instagram_URL,
        creatives.call_to_action_type AS call_to_action_type
    FROM
        {{ source('warehouse', 'meta_ads_ads') }} AS ads
    LEFT JOIN
        {{ source('warehouse', 'meta_ads_ad_creatives') }} AS creatives
    ON 
        (ads.creative::json->>'id') = creatives.id
),

renamed AS (
    SELECT 
        id AS "Ad_ID",           
        adset_id AS "Adset_ID",
        created_time AS "Created_At",
        updated_time AS "Updated_At",
        effective_status AS "Status",
        call_to_action_type AS "Call_To_Action",
        creative_url_image AS "Image_URL",
        Instagram_URL
    FROM 
        source
)

SELECT * FROM renamed