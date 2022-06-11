MSG_QUERY = """
with tx_data as (
select tx_id,msg_type
from osmosis.core.fact_msgs
  where block_id >= 4707300
  and block_id <= 4713064
  and (msg_type = 'pool_joined'
  or msg_type = 'pool_exited')
),
ready_data as (
select block_id, block_timestamp, tx_from, tx_status, t.msg_type
from osmosis.core.fact_transactions f
inner join tx_data t on t.tx_id=f.tx_id
  where block_id >= 4707300
  and block_id <= 4713064
)
select tx_from, msg_type, count(tx_status)
from ready_data
  where tx_status = 'SUCCEEDED'
  group by 1,2
order by 3 desc
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