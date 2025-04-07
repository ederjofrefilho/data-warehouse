with source as (
    select 
        id,
        adset_id,
        name,
        created_time,
        updated_time,
        effective_status,
        creative
    from
        {{ source ('warehouse', 'meta_ads_campaigns') }}
),

renamed as (
    select 
        account_id as "Account_ID",
        id as "Campaign_ID",
        name as "Campaign_Name",
        status as "Campaign_Status",
        objective as "Campaign_Objective",
        bid_strategy as "Campaign_Bid_Strategy",
        daily_budget as "Daily_Budget",
        lifetime_budget as "Lifetime_Budget",
        start_time as "Start_Time",
        stop_time as "Stop_Time"
    from 
        source
)

select * from renamed