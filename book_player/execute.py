# %%
import sqlalchemy
import datetime

from tqdm import tqdm

# %%

def dates_to_list(dt_start, dt_stop):
    date_start = datetime.datetime.strptime(dt_start, "%Y-%m-%d")
    date_stop = datetime.datetime.strptime(dt_stop, "%Y-%m-%d")
    days = (date_stop - date_start).days
    dates = [(date_start + datetime.timedelta(i)).strftime("%Y-%m-%d") for i in range(days+1)]
    return dates

def backfill(query, engine, dt_start, dt_stop):
    dates = dates_to_list(dt_start, dt_stop)
    for d in tqdm(dates):
        process_date(query, d, engine)

def import_query(path):
    with open(path, "r") as open_file:
        query = open_file.read()
    return query

def process_date(query, date, engine):
    delete = f"delete from tb_book_players where dtRef = '{date}'"
    engine.execute(delete)
    query = query.format(date = date)
    engine.execute(query)

# %%

engine = sqlalchemy.create_engine("sqlite:///../data/gc.db")

query = import_query("query.sql")

dt_start = input("Entre com uma data de início:")
dt_stop = input("Entre com uma data de fim:")

backfill(query, engine, dt_start, dt_stop)