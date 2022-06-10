import plotly.express as px
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, MaxNLocator
import seaborn as sns
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist
import streamlit as st


def plot_strip(data,x,y,scale=False):
    fig,ax = plt.subplots()
    sns.stripplot(data=data,x=x,y=y,ax=ax)
    if scale:
        plt.yscale('log')
    sns.despine()
    return fig


def plot_groups(data, groups):
    data['groups'] = groups
    data = data.query('groups!="C0"')
    s = data.groupby('groups').quantile(0.5)
    g1 = plot_strip(data,x='groups',y='minted',scale=True)
    g2 = plot_strip(data,x='groups',y='NFT_history',scale=False)
    g3 = plot_strip(data,x='groups',y='ETH_balance',scale=True)

    return g1,g2,g3,s

def cluster_plot(data):
    dist = pdist(data.values, metric='correlation')
    Z = hierarchy.linkage(dist, 'single')
    
    g = sns.clustermap(data.T.corr(),
        row_linkage=Z,
        col_linkage=Z,)
    den = hierarchy.dendrogram(g.dendrogram_col.linkage, labels=data.index,
                            color_threshold=0.10, distance_sort=True, ax=g.ax_col_dendrogram)
    g.ax_col_dendrogram.axis('on')
    # sns.despine(ax=g.ax_col_dendrogram, left=False, right=True, top=True, bottom=True)
    g.ax_col_dendrogram.yaxis.set_major_locator(MaxNLocator())
    g.ax_col_dendrogram.yaxis.set_major_formatter(ScalarFormatter())
    g.ax_col_dendrogram.grid(axis='y', ls='--', color='grey')
    # g.ax_col_dendrogram.yaxis.tick_right()
    
    groups = pd.Series(den['leaves_color_list'], index= [data.index[i] for i in den['leaves']])
    return g.fig, groups


def number_plot(df):
    fig,ax = plt.subplots()
    df.reset_index()['TOKENID'].plot(ax=ax)
    #plt.xticks([])
    plt.xlabel('Addresses')
    plt.ylabel('Number of NFTs Minted')
    sns.despine(fig=fig)
    return fig


def nft_plot(df):
    fig,ax = plt.subplots()
    df.reset_index()['NFT_ADDRESS'].plot(ax=ax)
    #plt.xticks([])
    plt.xlabel('Addresses')
    plt.ylabel('Number of NFTs Bought')
    sns.despine(fig=fig)
    return fig


def plot_scatter(df):
    i = df['USER_ADDRESS'].unique()[0]
    df['BALANCE_DATE'] = pd.to_datetime(df['BALANCE_DATE'])
    df['SYMBOL'] = df['SYMBOL'].fillna(df['CONTRACT_ADDRESS'])
    fig = px.scatter(df, x="BALANCE_DATE", y="BALANCE", color="SYMBOL",
                     color_discrete_sequence=px.colors.qualitative.G10,
                     template='simple_white',title=i,
                hover_data=['SYMBOL'],width=800, height=800)
    fig.update_layout(legend=dict(
    yanchor="top",
    y=-0.5,
    xanchor="left",
    x=0.01
))
    return fig

def eth_plot(df):
    fig,ax = plt.subplots()
    df.plot(x='USER_ADDRESS',y='BALANCE',ax=ax)
    plt.xticks([])
    plt.xlabel('Addresses')
    plt.ylabel('ETH balance')
    sns.despine()
    return fig