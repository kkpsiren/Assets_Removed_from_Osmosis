IMAGE_QUERY = """
with min_dt as (
  select min(block_timestamp) + interval '1 hour' as min_timestamp
  from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44' 
),
nft_data as (
select NFT_TO_ADDRESS, tokenid, block_timestamp
from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44'
  and block_timestamp <= (select min_timestamp from min_dt) 
order by 1 desc
  ),
nft_per_wallet as (
  select nft_to_address, count(tokenid)
  from nft_data
  group by 1
)
select buyer_address, nft_address, tokenid, price, m.token_metadata, m.token_metadata_uri, m.token_name, m.project_name, image_url
from ethereum.core.ez_nft_sales n
left join flipside_prod_db.ethereum.nft_metadata m on m.contract_address = nft_address and token_id=tokenid
where buyer_address in (select nft_to_address from nft_per_wallet)
and block_timestamp > getdate() - interval '6 months'
and  nft_address != '0x903e2f5d42ee23156d548dd46bb84b7873789e44'
and currency_symbol in ('WETH','ETH')
and price > 0
"""

SQL_QUERY = """
with min_dt as (
  select min(block_timestamp) + interval '1 hour' as min_timestamp
  from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44' 
),
nft_data as (
select NFT_TO_ADDRESS, tokenid, block_timestamp
from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44'
  and block_timestamp <= (select min_timestamp from min_dt) 
order by 1 desc
  ),
nft_per_wallet as (
  select nft_to_address, count(tokenid)
  from nft_data
  group by 1
)
select balance_date, user_address, label, contract_address, symbol, balance, amount_usd
from flipside_prod_db.ethereum.erc20_balances
where user_address in (select nft_to_address from nft_per_wallet)
and balance_date in ('2022-06-06','2022-06-07','2022-06-08')
    """
    
MINTED_QUERY = """
with min_dt as (
  select min(block_timestamp) + interval '1 hour' as min_timestamp
  from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44' 
),
nft_data as (
select NFT_TO_ADDRESS as USER_ADDRESS, tokenid, block_timestamp
from ethereum.core.ez_nft_mints
  where nft_address = '0x903e2f5d42ee23156d548dd46bb84b7873789e44'
  and block_timestamp <= (select min_timestamp from min_dt) 
order by 1 desc
)
select * from nft_data"""