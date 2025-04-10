with source as (
    select 
        campaign_id,
        id,
        name,
        created_time,
        updated_time,
        effective_status,
        bid_amount,
        targeting
    from
        {{ source('warehouse', 'meta_ads_ad_sets') }}
),

renamed as (
    select 
        cast(campaign_id as text) as "Campaign_ID",
        cast(id as text) as "AdSet_ID",
        cast(name as text) as "AdSet_Name",
        
        cast(created_time::date as date) as "Created_Date",
        cast(created_time::time as time) as "Created_Time",
        cast(updated_time::date as date) as "Updated_Date",
        cast(updated_time::time as time) as "Updated_Time",
        
        cast(effective_status as text) as "AdSet_Status",
        cast(bid_amount / 100.0 as numeric) as "Bid_Amount",
        
        cast((targeting ->> 'age_min') as integer) as "Age_Min",
        cast((targeting ->> 'age_max') as integer) as "Age_Max",

        (
            select string_agg(country, ', ')
            from jsonb_array_elements_text(targeting -> 'geo_locations' -> 'countries') as country
        ) as "Countries",

        (
            select string_agg(audience ->> 'name', ', ')
            from jsonb_array_elements(targeting -> 'custom_audiences') as audience
        ) as "Custom_Audience_Names",

        (targeting -> 'targeting_automation' ->> 'advantage_audience')::boolean as "Advantage_Audience"
        
    from 
        source
),

with_surrogate_key as (
    select 
        row_number() over () as "AdSet_Key",
        *
    from renamed
)

select * from with_surrogate_key
