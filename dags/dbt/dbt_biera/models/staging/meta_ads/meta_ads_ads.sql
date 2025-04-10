with source as (
    select
        ads.id,
        ads.adset_id,
        ads.created_time,
        ads.effective_status,
        ads.updated_time,
        creatives.image_url as creative_url_image,
        creatives.instagram_permalink_url as instagram_url,
        creatives.call_to_action_type as call_to_action_type
    from
        {{ source('warehouse', 'meta_ads_ads') }} as ads
    left join
        {{ source('warehouse', 'meta_ads_ad_creatives') }} as creatives
        on (ads.creative::json->>'id') = creatives.id
),

renamed as (
    select 
        cast(id as text) as "Ad_ID",           
        cast(adset_id as text) as "Adset_ID",
        cast(created_time::date as date) as "Created_Date",
        cast(created_time::time as time) as "Created_Time",
        cast(updated_time::date as date) as "Updated_Date",
        cast(updated_time::time as time) as "Updated_Time",
        cast(effective_status as text) as "Status",
        cast(call_to_action_type as text) as "Call_To_Action",
        cast(creative_url_image as text) as "Image_URL",
        cast(instagram_url as text) as "Instagram_URL"
    from 
        source
),

with_surrogate_key as (
    select 
        row_number() over () as "Ad_Key",
        *
    from renamed
)

select * from with_surrogate_key
