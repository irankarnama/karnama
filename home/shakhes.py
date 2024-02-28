from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import datetime
import pandas as pd
import time

import numpy as np
# from . import views


class es1(): #bulk dataset in elasticsearch

    def __init__(self):
        self.es1 = Elasticsearch(['address of elasticsearch es1'], http_auth=('es1 username', 'es1 password'),
                                      timeout=50)  # demo

    def Transfer_Index_From_ELK(self, Index_Name):
        scroll_size = 10000
        data = []
        resp = self.es1.search(
            index=Index_Name,
            scroll='2m',
            size=scroll_size,
            body={"query": {"match_all": {}}}
        )
        while len(resp['hits']['hits']) > 0:
            data += [hit['_source'] for hit in resp['hits']['hits']]
            resp = self.estehran.scroll(scroll_id=resp['_scroll_id'], scroll='2m')
        print("Fetched %d documents from %s" % (len(data), Index_Name))
        output = pd.DataFrame.from_dict(data)
        output = output.fillna(np.nan).replace([np.nan], [None])
        return output

    def bulk_sync(self, dictionaries, index_name):
        actions = [
            {
                "_index": index_name,
                "_source": dict,
                # "_id": dict[id]
            } for dict in dictionaries
        ]

        bulk(self.es1, actions)

    def Bulk_To_ELK(self, DataFrame, Index_Name):
        print('%s bulk started' % Index_Name)
        List_of_dicts = DataFrame.to_dict(orient='records')
        self.bulk_sync(List_of_dicts, Index_Name)  # Bulk (index all documents at once) to the ELK
        self.es1.indices.put_settings(index=Index_Name,
                                           body={
                                               "max_result_window": 1000000000})  # set maximum document fetching to 1B
        time.sleep(1)
        print('%s bulk finished' % Index_Name)

    def delete_index(self, index):
        self.Transfer_Index_From_ELK(index)
        self.es1.indices.delete(index=index, ignore=[400, 404])
        print('delete')
        time.sleep(2)
        
        
        
class es2(): #bulk dataset in elasticsearch

    def __init__(self):
        self.es2 = Elasticsearch(['address of elasticsearch es2'], http_auth=('es2 username', 'es2 password'),
                                      timeout=50)  # demo

    def Transfer_Index_From_ELK(self, Index_Name):
        scroll_size = 10000
        data = []
        resp = self.es1.search(
            index=Index_Name,
            scroll='2m',
            size=scroll_size,
            body={"query": {"match_all": {}}}
        )
        while len(resp['hits']['hits']) > 0:
            data += [hit['_source'] for hit in resp['hits']['hits']]
            resp = self.estehran.scroll(scroll_id=resp['_scroll_id'], scroll='2m')
        print("Fetched %d documents from %s" % (len(data), Index_Name))
        output = pd.DataFrame.from_dict(data)
        output = output.fillna(np.nan).replace([np.nan], [None])
        return output

    def bulk_sync(self, dictionaries, index_name):
        actions = [
            {
                "_index": index_name,
                "_source": dict,
                # "_id": dict[id]
            } for dict in dictionaries
        ]

        bulk(self.es1, actions)

    def Bulk_To_ELK(self, DataFrame, Index_Name):
        print('%s bulk started' % Index_Name)
        List_of_dicts = DataFrame.to_dict(orient='records')
        self.bulk_sync(List_of_dicts, Index_Name)  # Bulk (index all documents at once) to the ELK
        self.es1.indices.put_settings(index=Index_Name,
                                           body={
                                               "max_result_window": 1000000000})  # set maximum document fetching to 1B
        time.sleep(1)
        print('%s bulk finished' % Index_Name)

    def delete_index(self, index):
        self.Transfer_Index_From_ELK(index)
        self.es1.indices.delete(index=index, ignore=[400, 404])
        print('delete')
        time.sleep(2)


class anbar():
    Connectionte = es1()
    Connectionmo = es2()

    def Depletion(self, day):  # چی بخریم تا خط تولید نخوابیده
        print('Warehouse depletion computation started')
        today = datetime.datetime.now()
        # jalali_year = jdatetime.date.today().year
        # columns = ['idanbar', 'anbarname', 'kalaname', 'idkala', 'ted', 'time', 'unit', 'fi']
        agg_condition = {
            'ted': 'sum',
            'idanbar': 'max',
            'anbarname': lambda x: x.iloc[0],  # This will keep the first value of 'anbarname' in the group
            'idkala': 'max',
            'unit': lambda x: x.iloc[0],  # This will keep the first value of 'unit' in the group
            'fi': 'max',
            'time': 'max'
        }

        # self.Connectionmo.indices.put_settings(index='sain_kardex_kol_%s' %jalali_year, body={"max_result_window": 1000000000})                          # set maximum document fetching to 1B
        # time.sleep(1)
        warehouse = pd.DataFrame()
        warehouse = self.Connectionmo.Transfer_Index_From_ELK('sain_kardex_kol_1402')

        warehouse['ted'] = warehouse['ted'].astype(int)
        warehouse['fi'] = warehouse['fi'].astype(int)

        warehouse['time'] = pd.to_datetime(warehouse['time'])
        last_month_consumption = warehouse.loc[
            (warehouse['time'] >= (today - datetime.timedelta(days=day))) & (warehouse['ted'] < 0)]
        last_month_consumption = last_month_consumption.groupby('kalaname', sort=False).agg(agg_condition)
        warehouse = warehouse.groupby('kalaname', sort=False).agg(agg_condition)
        warehouse = warehouse.loc[warehouse.index.isin(last_month_consumption.index)][['ted']].rename(
            columns={'ted': 'ted_kol'})  # The amount of stuffs which are available in the warehouse at this moment

        last_month_consumption = last_month_consumption.join(warehouse)
        last_month_consumption['needed_ted_month'] = -1 * last_month_consumption['ted']
        last_month_consumption['needed_money'] = -(last_month_consumption['ted'] * last_month_consumption['fi'])
        last_month_consumption['ted'] = last_month_consumption['ted'] * 7 / 30 + last_month_consumption['ted_kol']
        # del last_month_consumption['ted_kol']
        last_month_consumption['color'] = last_month_consumption['ted'].apply(lambda x: 'Green' if x >= 0 else 'Red')

        last_month_consumption['id'] = (today.year * 10 ** 4 + today.month * 10 ** 2 + today.day) * 10 ** 6 + \
                                       last_month_consumption['idanbar'] * 10 ** 3 + last_month_consumption['idkala']
        last_month_consumption = last_month_consumption.reset_index().rename(columns={'index': 'kalaname'})
        last_month_consumption['time'] = today
        return last_month_consumption['ted'], last_month_consumption['needed_money']
