# %%
import pandas as pd
import sqlalchemy

from sklearn import model_selection
from sklearn import ensemble

from sklearn import pipeline
from sklearn import metrics

from feature_engine import imputation
from feature_engine import encoding

def report_model(X, y, model, metric, is_prob=True):
    if is_prob:
        y_pred = model.predict_proba(X)[:,1]
    
    else:
        y_pred = model.predict(X)
    res = metric(y, y_pred)
    return res

# %%
# SAMPLE

print("Importando ABT...")
con = sqlalchemy.create_engine("sqlite:///../../../data/gc.db")
df = pd.read_sql_table("tb_abt_sub", con)
print("ok.")

# Nosso back-test
print("Separando entre treinamento e Backtest...")
df_oot = df[df["dtRef"].isin(['2022-01-15','2022-01-16'])].copy()
df_train = df[~df["dtRef"].isin(['2022-01-15','2022-01-16'])].copy()
print("ok.")

features = df_train.columns.tolist()[2:-1]
target = 'flagSub'

print("Separando entre Treino e Test...")
X_train, X_test, y_train, y_test = model_selection.train_test_split(df_train[features],
                                                                    df_train[target],
                                                                    random_state=42,
                                                                    test_size=0.2)

print("ok.")
# %%
# EXPLORE

cat_features = X_train.dtypes[X_train.dtypes=='object'].index.tolist()
num_features = list(set(X_train.columns) - set(cat_features))

# %%
print("Estatística de missings")
print("    Missing numerico")
is_na = X_train[num_features].isna().sum()
print(is_na[is_na>0])

missing_0 = ["avgKDA",]

missing_1 = ["vlIdade",
             "winRateDust2",
             "winRateNuke",
             "winRateOverpass",
             "winRateVertigo",
             "winRateTrain",
             "winRateMirage",
             "winRateInferno",
             "winRateAncient", ]


# %%
print("\n    Missing numerico")
is_na = X_train[cat_features].isna().sum()
print(is_na[is_na>0])

print("ok.")
# %%

# MODIFY

print("Construindo pipeline de ML...")
## imputação de dados
imput_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0, variables=missing_0)
imput_1 = imputation.ArbitraryNumberImputer(arbitrary_number=-1, variables=missing_1)

## one hot encoding
onehot = encoding.OneHotEncoder(drop_last=True, variables=cat_features)

# MODEL

rf_clf = ensemble.RandomForestClassifier(n_estimators=200,
                                         min_samples_leaf=20,                                        
                                         n_jobs=-1,
                                         random_state=42)

## Definir um pipeline

params = {"n_estimators":[200,250],
          "min_samples_leaf": [5,10,20] }

grid_search = model_selection.GridSearchCV(rf_clf, params, n_jobs=1, cv=4, scoring='roc_auc', refit=True)

pipe_rf = pipeline.Pipeline(steps = [("Imput 0", imput_0),
                                     ("Imput -1", imput_1),
                                     ("One Hot", onehot),
                                     ("Modelo", grid_search)])

print("ok.")

print("Encontrando o melhor modelo com grid search...")
pipe_rf.fit(X_train, y_train)
print("ok")

# %%

auc_train = report_model(X_train, y_train, pipe_rf, metrics.roc_auc_score)
auc_test = report_model(X_test, y_test, pipe_rf, metrics.roc_auc_score)
auc_oot = report_model(df_oot[features], df_oot[target], pipe_rf, metrics.roc_auc_score)

print("auc_train:", auc_train)
print("auc_test:", auc_test)
print("auc_oot:", auc_oot)

# %%

print("Ajustar modelo para base toda...")

pipe_model = pipeline.Pipeline(steps = [("Imput 0", imput_0),
                                        ("Imput -1", imput_1),
                                        ("One Hot", onehot),
                                        ("Modelo", grid_search.best_estimator_)])

pipe_model.fit(df[features], df[target])

print("ok")

# %%

print("Feature importance by model...")
features_transformed = pipe_model[:-1].transform(df[features]).columns.tolist()
features_importances = pd.DataFrame(pipe_model[-1].feature_importances_, index=features_transformed)
features_importances.sort_values(by=0, ascending=False)
print("ok.")

# %%

series_model = pd.Series({
    "model":pipe_model,
    "features":features,
    "auc_train":auc_train,
    "auc_test":auc_test,
    "auc_oot":auc_oot,
})

series_model.to_pickle("../../../models/modelo_subscription.pkl")
# %%
