with source as (
    select 
        id,
        created_time,
        name,
        status,
        objective,
        bid_strategy,
        account_id,
        start_time,
        stop_time,
        daily_budget,
        lifetime_budget
    from
        {{ source('warehouse', 'meta_ads_campaigns') }}
),

renamed as (
    select 
        cast(account_id as text) as "Account_ID",
        cast(id as text) as "Campaign_ID",
        cast(name as text) as "Campaign_Name",
        cast(status as text) as "Campaign_Status",
        cast(objective as text) as "Campaign_Objective",
        cast(bid_strategy as text) as "Campaign_Bid_Strategy",
        cast(daily_budget / 100.0 as numeric) as "Daily_Budget",
        cast(lifetime_budget / 100.0 as numeric) as "Lifetime_Budget",
        cast(start_time::date as date) as "Start_Date",
        cast(start_time::time as time) as "Start_Time",
        cast(stop_time::date as date) as "Stop_Date",
        cast(stop_time::time as time) as "Stop_Time"
    from 
        source
),

with_surrogate_key as (
    select 
        row_number() over () as "Campaign_Key",
        *
    from renamed
)

select * from with_surrogate_key
