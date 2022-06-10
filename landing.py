import streamlit as st

from plots import number_plot, eth_plot, nft_plot, cluster_plot, plot_groups

def get_groups(data,groups):
    data['groups'] = groups
    data['groups'] = data['groups'].str.replace("C0","C1")
    ans = [y for x, y in data.groupby('groups', as_index=False)]
    return ans
        

def landing_page(df,df_minted,df_images):
    st.image('https://openseauserdata.com/files/e22c98856cf40d4efb9d2dcb69d25c9b.png')
    st.write("GodMode by FlipsideCrypto")
    st.markdown(
        """
        ### Analyze the Ethereum profile of those who minted during the first hour after launch. 
        146 addresses minted 264 NFTs during the first hour
        """ 
    )
    ser = df_minted.groupby('USER_ADDRESS')['TOKENID'].count().sort_values(ascending=False)
    l,r = st.columns(2)
    with r:
        st.pyplot(number_plot(ser),use_container_width=True)
    with l:
        for i,val in ser.iloc[:7].iteritems():
            address = f'https://etherscan.io/address/{i}'
            st.markdown(f'[{i[:7]}...{i[-5:]}]({address})  Minted {val} GodMode NFTs')
        st.write(f'rest of the {264-7} remaining also minted 1 GodMode NFT. See the individual address page for the full list')


    eth_df = df.query('SYMBOL=="ETH"')
    ser = eth_df.query("BALANCE_DATE=='2022-06-07'").sort_values('BALANCE',ascending=False)
    st.markdown(f"""
                
                        
### How many of them moved the minimum .1 ETH into their minting wallet vs. already had at least .1 ETH in that wallet? 
{(ser['BALANCE']>1).sum()} addresses had more than 1 ETH  
{(ser['BALANCE']>0.1).sum()} addresses had more than 0.1 ETH  
{(ser['BALANCE']>0.01).sum()} addresses had more than 0.01 ETH  
""")
    

    l,r = st.columns(2)
    with r:
        st.pyplot(eth_plot(ser),use_container_width=True)
    with l:
        #st.dataframe(ser)
        for i, val in ser.iloc[:7,:].iterrows():
            address = f'https://etherscan.io/address/{val["USER_ADDRESS"]}'
            # st.write(val)
            st.markdown(f'[{val["USER_ADDRESS"][:7]}...{val["USER_ADDRESS"][-5:]}]({address}) Had {val["BALANCE"]:.5f} ETH on 2022-06-07 ')
        #st.write(f'rest of the {df.shape[0]-7} also minted 1. See the individual address page for the full list')


    st.markdown(f"""             
             ### How many of them have been active in NFT purchases over the past six months? 
             
             """)

    ser = df_images.groupby('BUYER_ADDRESS')['NFT_ADDRESS'].count().sort_values(ascending=False)
    l,r = st.columns(2)
    with r:
        st.pyplot(nft_plot(ser),use_container_width=True)
    with l:
        for i,val in ser.iloc[:7].iteritems():
            address = f'https://etherscan.io/address/{i}'
            st.markdown(f'[{i[:7]}...{i[-5:]}]({address})  Minted {val} GodMode NFTs')
        st.write(f'In total 48 addresses have minted an NFT that cost more than 0 ETH or WETH.')
        with st.expander("show addresses"):
            for i in ser.index.tolist():
                st.markdown(f'[{i}](https://etherscan.io/address/{i})')



    ser = df_images.groupby('BUYER_ADDRESS')['NFT_ADDRESS'].count().to_frame('NFT_history')

    a = df.query('SYMBOL=="ETH"')
    ser2 = a[a['BALANCE']>0.1].groupby('USER_ADDRESS')['BALANCE'].mean().to_frame('ETH_balance')

    ser3 = df_minted.groupby('USER_ADDRESS')['TOKENID'].count().to_frame('minted')

    data = ser3.join(ser2).join(ser).fillna(0)
    with st.spinner('Wait for it...'):
        fig, groups = cluster_plot(data)
    st.markdown(""" ### Can you construct a “typical minter” profile/profiles based on their wallet behavior?""")
    st.pyplot(fig,use_container_width=True)
    st.markdown("""By plotting the ETH amounts, NFT history and number of minted NFTS, 
                and computing the correlation of all the addresses we can form four groups, C1-C4. 
                1. C1 9 addresses belong to this group, Their median ETH balance is 6.27 ETH. They have both a single NFT as median.  
                2. C2 These are the burner addresses. 40 % of the members own less than 0.1 ETH before minting. No NFT Purchasing history as median. 96 Addresses belong to this group.  
                3. C3 These are also burner addresses. They own same amount of ETH than C2 but they have a single NFT Purchase as median. 10 Addresses belong to this group.  
                4. C4 31 addresses belong to this group. They have a median ETH balance of 0.4 ETH and 10 NFTs purchased on median.
                """)
    g1,g2,g3,s = plot_groups(data,groups)
    l1,l2,l3 = st.columns(3)
    ans = get_groups(data,groups)
    cols = "minted,ETH_balance,NFT_history,groups,USER_ADDRESS".split(',')
    
    with l1:
        st.pyplot(g1,use_container_width=True)
        with st.expander('Show DataFrame'):
            st.dataframe(ans[0].reset_index().loc[:,cols])
    with l2:
        st.pyplot(g2,use_container_width=True)
        with st.expander('Show DataFrame'):
            st.dataframe(ans[1].reset_index().loc[:,cols])
    with l3:
        st.pyplot(g3,use_container_width=True)
        with st.expander('Show DataFrame'):
            st.dataframe(ans[2].reset_index().loc[:,cols])
    st.write('Median Values')
    st.dataframe(s)
    
    
    st.write('More Analysis on these and the whole mint and aftermarket TBC')