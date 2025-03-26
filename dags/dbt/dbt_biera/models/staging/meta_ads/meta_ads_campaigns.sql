with source as (
    select 
        id,
        created_time,
        name,
        status,
        objective,
        bid_strategy

    from
        {{ source ('warehouse', 'meta_ads_campaigns') }}
),

renamed as (
    select 
        id as "Campaign_ID",
        name as "Campaign_Name",
        status as "Campaign_Status",
        objective as "Campaign_Objective",
        bid_strategy as "Campaign_Bid_Strategy" 
    from 
        source
)

select * from renamed