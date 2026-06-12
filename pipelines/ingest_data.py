#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd

# In[18]:


prefix = "https://github.com/AxisTrotec/global_energy_data/releases/download/data/global_power_plant_database.csv"


# In[19]:


dtype = {
    "country": "string",
    "country_long": "string",
    "name": "string",
    "gppd_idnr": "string",
    "capacity_mw": "float64",
    "latitude": "float64",
    "longitude": "float64",
    "primary_fuel": "string",
    "other_fuel1": "string",
    "other_fuel2": "string",
    "other_fuel3": "string",
    "commissioning_year": "float64",
    "owner": "string",
    "source": "string",
    "url": "string",
    "geolocation_source": "string",
    "wepp_id": "string",
    "year_of_capacity_data": "float64",
    "generation_gwh_2013": "float64",
    "generation_gwh_2014": "float64",
    "generation_gwh_2015": "float64",
    "generation_gwh_2016": "float64",
    "generation_gwh_2017": "float64",
    "generation_gwh_2018": "float64",
    "generation_gwh_2019": "float64",
    "generation_data_source": "string",
    "estimated_generation_gwh_2013": "float64",
    "estimated_generation_gwh_2014": "float64",
    "estimated_generation_gwh_2015": "float64",
    "estimated_generation_gwh_2016": "float64",
    "estimated_generation_gwh_2017": "float64",
    "estimated_generation_note_2013": "string",
    "estimated_generation_note_2014": "string",
    "estimated_generation_note_2017": "string",
    "estimated_generation_note_2015": "string",
    "estimated_generation_note_2016": "string"
}


# In[20]:


df = pd.read_csv(prefix, sep=',', encoding='utf-8', dtype=dtype, nrows=100)


# In[21]:


df.head()


# In[22]:


df.dtypes


# In[23]:


from sqlalchemy import create_engine


# In[24]:


engine = create_engine('postgresql+psycopg://{user}:{password}@{host}:{port}/{db}')


# In[25]:


print(pd.io.sql.get_schema(df, name='energy_data', con=engine))


# In[26]:


df.head(n=0).to_sql(name='energy_data', con=engine, if_exists='replace')


# In[27]:


df_iter = pd.read_csv(
    prefix,
    dtype=dtype,
    iterator=True,
    chunksize=100000
)


# In[29]:

from tqdm.auto import tqdm
import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='energy_data', help='PostgreSQL database name')
@click.option('--target-table', default='energy_data', help='Target table name')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    first = True

    for df_chunk in tqdm(df_iter):

        if first:
            # Create table schema (no data)
            df_chunk.head(0).to_sql(
                name="energy_data",
                con=engine,
                if_exists="replace"
            )
            first = False
            print("Table created")

        # Insert chunk
        df_chunk.to_sql(
            name="energy_data",
            con=engine,
            if_exists="append"
        )

        print("Inserted:", len(df_chunk))



# In[ ]:




