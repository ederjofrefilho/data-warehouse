with source as (
    select 
        "Day",
        "Ad_ID",
        "Leads",
        "Reach",
        "Results",
        "Ad_Set_ID",
        "Target_ID",
        "Campaign_ID",
        "Impressions",
        "Link_Clicks",
        "Amount_Spent",
        "Clicks__All_"
    from
        {{ source('warehouse', 'meta_ads_desempenho') }}
),

renamed as (
    select 
        cast("Day" as date) as "Day",
        cast("Ad_ID" as text) as "Ad_ID",
        cast("Leads" as integer) as "Leads",
        cast("Reach" as integer) as "Reach",
        cast("Results" as integer) as "Results",
        cast("Ad_Set_ID" as text) as "Ad_Set_ID",
        cast("Target_ID" as text) as "Target_ID",
        cast("Campaign_ID" as text) as "Campaign_ID",
        cast("Impressions" as integer) as "Impressions",
        cast("Link_Clicks" as integer) as "Link_Clicks",
        cast("Amount_Spent" as numeric) as "Amount_Spent",  -- Dividido por 100 para representar valores monetários
        cast("Clicks__All_" as integer) as "Clicks_All"
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
