import streamlit as st

from plots import number_plot, eth_plot, nft_plot, cluster_plot, plot_groups

def get_groups(data,groups):
    data['groups'] = groups
    data['groups'] = data['groups'].str.replace("C0","C1")
    ans = [y for x, y in data.groupby('groups', as_index=False)]
    return ans
        

def landing_page(df,df_minted,df_images):
    st.image('https://openseauserdata.com/files/e22c98856cf40d4efb9d2dcb69d25c9b.png')
    st.markdown("""## Assets Removed from Osmosis 
supported by GodMode by FlipsideCrypto""")
    st.markdown(
        """
On June 8th, a critical bug was found on Osmosis that led to the theft of several million dollars from liquidity pools. In an effort to help provide the Osmosis team with important data, we’ve curated these flash bounties to surface metrics that the team has requested. The upgrade that contained the exploited bug occurred at block height 4707300, and the chain was halted at block 4713064.

What was the total dollar amount of assets that was improperly removed from pools due to the bug, 

and what is the list of addresses that had joined a pool since the upgrade? 

What is the dollar value deposited of those addresses joining pools? 

What is the cumulative value of funds that joined and exited?

Hints: addresses that run the MsgJoinPool & MsgExitPool message types
        """ 
    )