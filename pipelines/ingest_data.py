#!/usr/bin/env python
from tqdm.auto import tqdm
from sqlalchemy import create_engine

import click
import pandas as pd

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='energy_data', help='PostgreSQL database name')
@click.option('--target-table', default='energy_data', help='Target table name')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    prefix = "https://github.com/AxisTrotec/global_energy_data/releases/download/data/global_power_plant_database.csv"

    first = True

    port = int(pg_port) 
    
    # Use the variables inside the connection string
    connection_url = f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{port}/{pg_db}'
    engine = create_engine(connection_url)
    
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

    df = pd.read_csv(prefix, sep=',', encoding='utf-8', dtype=dtype, nrows=100)


    print(pd.io.sql.get_schema(df, name='energy_data', con=engine))

    df.head()

    df.dtypes

    df.head(n=0).to_sql(name='energy_data', con=engine, if_exists='replace')

    df_iter = pd.read_csv(
        prefix,
        dtype=dtype,
        iterator=True,
        chunksize=100000
    )


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



run()