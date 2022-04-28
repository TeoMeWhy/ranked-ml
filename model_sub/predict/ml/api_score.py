import sqlalchemy
import pandas as pd

with open("../etl/query_id.sql", "r") as open_file:
    query = open_file.read()

con = sqlalchemy.create_engine("sqlite:///../../../data/gc.db")
model = pd.read_pickle("../../../models/modelo_subscription.pkl")

def score(id_player):
    df = pd.read_sql(query.format(id_player=id_player), con)
    score = model['model'].predict_proba( df[model["features"]] )[:,1][0]
    return score