import streamlit as st
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
import plotly.express as px
cm = sns.light_palette("green", as_cmap=True)

def load_evidence():
    df = pd.read_csv('data/evidence.csv',sep=',')
    #"cols = df.columns[0].split(',')
    #"df = df[df.columns[0]].str.split(',',expand=True).iloc[:,0:len(cols)]
    #"df.columns = cols
    df2 = df.query('MSG_KEY=="pool_id"').copy()
    df2['MSG_VALUE'] = df2['MSG_VALUE'].astype('int').copy()
    df = df.drop(df2.index)
    df = df.drop('MSG_VALUE',axis=1)
    df['BLOCK_TIMESTAMP'] = pd.to_datetime(df['BLOCK_TIMESTAMP'])
    df['ASSET1_USD'] = df['ASSET1_AMOUNT'] * df['ASSET1_PRICE']
    df['ASSET2_USD'] = df['ASSET2_AMOUNT'] * df['ASSET2_PRICE']

    df['dummy'] = 1
    df['POOL_ID'] = df['TX_ID'].map(df2.groupby('TX_ID')['MSG_VALUE'].first())
    df['USD'] = df['ASSET1_USD'] + df['ASSET2_USD']
    return df

def inandout(ser):
    msg_type = ser['MSG_KEY']
    usd = ser['USD']
    #print(msg_type)
    if 'in' in msg_type:
        return usd
    elif 'out' in msg_type:
        return -1*usd
    else:
        return 0
    
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
 
def landing_page():
    st.image('https://openseauserdata.com/files/e22c98856cf40d4efb9d2dcb69d25c9b.png')
    st.markdown("""## Assets Removed from Osmosis 
supported by GodMode by FlipsideCrypto""")
    st.markdown(
        """
On June 8th, a critical bug was found on Osmosis that led to the theft of several million dollars from liquidity pools. In an effort to help provide the Osmosis team with important data, we’ve curated these flash bounties to surface metrics that the team has requested. The upgrade that contained the exploited bug occurred at block height 4707300, and the chain was halted at block 4713064.
    """)

    df = load_evidence()
    d = df.groupby(['POOL_ID','MSG_KEY'])['USD'].sum().sort_values(ascending=False).reset_index()
    d = d.pivot(index='POOL_ID',columns='MSG_KEY',values='USD').fillna(0)
    d['difference'] = d['tokens_out'] - d['tokens_in'] 
    d = d.sort_values(by='difference',ascending=False)
    d = d.query('difference>0')
    
    
    st.markdown(f"""
## What was the total dollar amount of assets that was improperly removed from pools due to the bug, """)
    option_slider = st.slider('USD Value lost', min_value=None, max_value=25000, value=1000)
    d1 = d.query('difference>=@option_slider')
    l,r = st.columns(2)
    with l:
        st.markdown(f"""
In total {d.shape[0]} have lost USD. However   
overall {d1.shape[0]} pools lost at least {option_slider} USD.  
Totaling {d1['difference'].sum():.0f} USD
    """)
    with r:
        d_plotly = d.query('difference>=@option_slider').reset_index()
        d_plotly['POOL_ID'] = d_plotly['POOL_ID'].astype('str')
        fig = px.bar(d_plotly, x='POOL_ID', y='difference',log_y=True,
                     hover_data=['POOL_ID','tokens_in','tokens_out','difference'])
        st.plotly_chart(fig,use_container_width=True)
    with st.expander('Show Full Data'):
        st.dataframe(d)
    #fig,ax =plt.subplots()
    #sns.heatmap(d, ax=ax)
    #st.pyplot(fig)
    

    # tähän poolit ja dollarit ja määrät
    
    
    
    st.markdown(f"""
## and what is the list of addresses that had joined a pool since the upgrade?  
""")
    option_slider2 = st.slider('min deposit amount in USD', min_value=0, max_value=25000, value=0)
    data = df.query('(MSG_KEY=="tokens_in")').groupby('SENDER')['USD'].sum().reset_index()
    data = data.query('USD>=@option_slider2')
    senders = data['SENDER'].unique()
    st.markdown(f"""
In total there are {len(senders)} unique addresses that have joined a pool since the upgrade
    """)
    with st.expander('show list'):
        st.dataframe(data.sort_values(by='USD',ascending=False).style.background_gradient(cmap=cm))
    csv = convert_df(data.merge(df.query('MSG_KEY=="tokens_in"').groupby('SENDER')['TX_ID'].first().to_frame(),on='SENDER',how='left').sort_values(by='USD',ascending=False))
    st.download_button(
     label="Download data as CSV",
     data=csv,
     file_name='addresses_that_have_joined_pools_since_blockid_4707300.csv',
     mime='text/csv',
 )
    
    st.markdown(f"""
## What is the dollar value deposited of those addresses joining pools? 

In total {data['USD'].sum():.0f} USD
    """)

    
    with st.expander('Breakdown by Address'):
        st.dataframe(data.sort_values(by='USD',ascending=False).style.background_gradient(cmap=cm))
    
    st.markdown("""
## What is the cumulative value of funds that joined and exited?
        """ 
    )
    df['val'] = df.apply(inandout,axis=1)
    df = df.sort_values('BLOCK_TIMESTAMP')
    df['Cumulative USD Value of Funds'] = df['val'].cumsum()
    df['POOL_ID'] = df['POOL_ID'].astype('str')
    fig = px.scatter(df, 
                        x="BLOCK_TIMESTAMP", 
                        y="Cumulative USD Value of Funds", 
                        color="POOL_ID",
                    color_discrete_sequence=px.colors.qualitative.G10,
                    template='simple_white',
                hover_data=['SENDER','MSG_KEY','BLOCK_TIMESTAMP',"POOL_ID",
    'ASSET1_SYMBOL', 'ASSET1_AMOUNT', 'ASSET2_SYMBOL', 'ASSET2_AMOUNT',
    'TX_ID'],width=800, height=500)
    fig.update_layout(legend=dict(
                    yanchor="top",
                    y=.5,
                    xanchor="left",
                    #legend_orientation="h",
                    x=1.1
                    ))
    
    
    st.markdown(f"Cumulative value that has entered / exited is {df.dropna().iloc[-1]['Cumulative USD Value of Funds']:.0f} USD")

    st.plotly_chart(fig)
    
    with st.expander("Per Pool"):
        selected_pool = st.selectbox('Select Pool ID', sorted(d_plotly['POOL_ID'].unique()), index=0)
        df_pool = df.query('POOL_ID==@selected_pool').sort_values('BLOCK_TIMESTAMP')
        df_pool[f'Cumulative USD Value of Funds Pool {selected_pool}'] = df_pool['val'].cumsum()
        df_pool['POOL_ID'] = df_pool['POOL_ID'].astype('str')
        fig = px.scatter(df_pool, 
                            x="BLOCK_TIMESTAMP", 
                            y=f'Cumulative USD Value of Funds Pool {selected_pool}', 
                            color="SENDER",
                        color_discrete_sequence=px.colors.qualitative.G10,
                        template='simple_white',
                    hover_data=['SENDER','MSG_KEY','BLOCK_TIMESTAMP',"POOL_ID",
        'ASSET1_SYMBOL', 'ASSET1_AMOUNT', 'ASSET2_SYMBOL', 'ASSET2_AMOUNT',
        'TX_ID'],width=800, height=500)
        fig.update_layout(legend=dict(
                        yanchor="top",
                        y=.5,
                        xanchor="left",
                        #legend_orientation="h",
                        x=1.1
                        ))
        st.markdown(f"Cumulative value that has entered / exited is {df_pool.iloc[-1][f'Cumulative USD Value of Funds Pool {selected_pool}']:.0f} USD")
        st.plotly_chart(fig)
    
    st.markdown(f""" ## Conclusion
                
Most of the exploit has happened via Pool 1. Other affected pools are 497, 498, 585 and 13.  
Only 5 users have deposited more than 2000USD since the upgrade. These could be the exploiters.


### Queries used
[osmosis_exploit_pool_id](https://app.flipsidecrypto.com/velocity/queries/64d13ffd-9e10-48fb-896f-1ac3965d832b)  

### Github
[kkpsiren/Bug_Exploiters](https://github.com/kkpsiren/Bug_Exploiters)
    """)