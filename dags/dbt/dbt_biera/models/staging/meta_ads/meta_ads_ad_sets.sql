with source as (
    select 
        campaign_id,
        id,
        name,
        created_time,
        updated_time,
        effective_status,
        bid_amount,
        targeting  -- Coluna JSON adicionada

    from
        {{ source ('warehouse', 'meta_ads_ad_sets') }}
),

renamed as (
    select 
        campaign_id as "Campaign_ID",
        id as "AdSet_ID",
        name as "AdSet_Name",
        created_time as "Created_At",
        updated_time as "Last_Update",
        effective_status as "AdSet_Status",
        bid_amount as "Bid_Amount",
        
        -- Extraindo campos do JSON
        (targeting ->> 'age_min')::integer as "Age_Min",
        (targeting ->> 'age_max')::integer as "Age_Max",
        
        -- Países como lista separada por vírgulas
        (
            select string_agg(country, ', ')
            from jsonb_array_elements_text(targeting -> 'geo_locations' -> 'countries') as country
        ) as "Countries",
        
        -- Nomes das audiências customizadas
        (
            select string_agg(audience ->> 'name', ', ')
            from jsonb_array_elements(targeting -> 'custom_audiences') as audience
        ) as "Custom_Audience_Names",
        
        -- Advantage Audience como booleano
        (targeting -> 'targeting_automation' ->> 'advantage_audience')::integer = 1 as "Advantage_Audience"

    from 
        source
)

select * from renamed