import requests
import json
import time
import os
from dotenv import load_dotenv
import pandas as pd 
from queries import * 
import streamlit as st
load_dotenv()

class Flipsider:
    def __init__(self, API_KEY, TTL_MINUTES=15):
        self.API_KEY = API_KEY
        self.TTL_MINUTES = TTL_MINUTES

    def create_query(self, SQL_QUERY):
        r = requests.post(
            'https://node-api.flipsidecrypto.com/queries', 
            data=json.dumps({
                "sql": SQL_QUERY,
                "ttlMinutes": self.TTL_MINUTES
            }),
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": self.API_KEY},
        )
        if r.status_code != 200:
            raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))

        return json.loads(r.text)    


    def get_query_results(self, token):
        r = requests.get(
            'https://node-api.flipsidecrypto.com/queries/' + token, 
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": self.API_KEY}
        )
        if r.status_code != 200:
            raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))
        
        data = json.loads(r.text)
        if data['status'] == 'running':
            time.sleep(10)
            return self.get_query_results(token)

        return data


    def run(self, SQL_QUERY):
        query = self.create_query(SQL_QUERY)
        token = query.get('token')
        data = self.get_query_results(token)
        df = pd.DataFrame(data['results'],columns = data['columnLabels'])
        return df

@st.cache()
def load_queries():
    bot = Flipsider(os.getenv('API_KEY'))
    df = bot.run(SQL_QUERY)
    df_images = bot.run(IMAGE_QUERY)
    df_minted = bot.run(MINTED_QUERY)
    return df, df_images, df_minted

if __name__ == '__main__':
    bot = Flipsider(os.getenv('API_KEY'))
    

    df = bot.run(SQL_QUERY)
    df_images = bot.run(IMAGE_QUERY)

    #df_ = df.pivot_table(index='CONTRACT_ADDRESS',columns='SYMBOL',values='BALANCE',aggfunc='min')
    #df_ = ~df_.isnull()
    df_ = df[df['SYMBOL']=='ETH'].sort_values('BALANCE')
    mapper = {i:f'address_{j}' for j,i in enumerate(df_['USER_ADDRESS'].unique())}
    df_['address'] = df_['USER_ADDRESS'].map(mapper)
    
    df_.groupby('USER_ADDRESS')['BALANCE'].max().quantile(0.25)
    
    sns.scatterplot(data=df_,x='BALANCE_DATE',y='BALANCE',color='address')