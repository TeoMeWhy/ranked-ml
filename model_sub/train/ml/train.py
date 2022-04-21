# %%
from types import MethodWrapperType
import pandas as pd
import sqlalchemy

import matplotlib.pyplot as plt

from sklearn import model_selection
from sklearn import ensemble
from sklearn import pipeline
from sklearn import metrics

from feature_engine import imputation
from feature_engine import encoding

import scikitplot as skplt

pd.set_option('display.max_columns', None)
# %%
# SAMPLE

con = sqlalchemy.create_engine("sqlite:///../../../data/gc.db")
df = pd.read_sql_table("tb_abt_sub", con)

# Nosso back-test
df_oot = df[df["dtRef"].isin(['2022-01-15','2022-01-16'])].copy()
df_train = df[~df["dtRef"].isin(['2022-01-15','2022-01-16'])].copy()

features = df_train.columns.tolist()[2:-1]
target = 'flagSub'

X_train, X_test, y_train, y_test = model_selection.train_test_split(df_train[features],
                                                                    df_train[target],
                                                                    random_state=42,
                                                                    test_size=0.2)


# %%
# EXPLORE

cat_features = X_train.dtypes[X_train.dtypes=='object'].index.tolist()
num_features = list(set(X_train.columns) - set(cat_features))

# %%

print("Missing numerico")
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

print("Missing numerico")
is_na = X_train[cat_features].isna().sum()
print(is_na[is_na>0])

# %%

# MODIFY

## imputação de dados
imput_0 = imputation.ArbitraryNumberImputer(arbitrary_number=0, variables=missing_0)
imput_1 = imputation.ArbitraryNumberImputer(arbitrary_number=-1, variables=missing_1)

## one hot encoding
onehot = encoding.OneHotEncoder(drop_last=True, variables=cat_features)

# MODEL

model = ensemble.RandomForestClassifier(n_estimators=200,
                                        min_samples_leaf=20,                                        
                                        n_jobs=-1)

## Definir um pipeline

model_pipe = pipeline.Pipeline(steps = [("Imput 0", imput_0),
                                        ("Imput -1", imput_1),
                                        ("One Hot", onehot),
                                        ("Modelo", model)])

# %%

model_pipe.fit(X_train, y_train)

# %%


## Assess
y_train_pred = model_pipe.predict(X_train)
y_train_prob = model_pipe.predict_proba(X_train)

acc_train = round(100*metrics.accuracy_score(y_train, y_train_pred),2)
roc_train = metrics.roc_auc_score(y_train, y_train_prob[:,1] )
print("acc_train:", acc_train)
print("roc_train:", roc_train)

# %%

print("Baseline: ", round((1-y_train.mean())*100,2))
print("Acurácia:", acc_train)

# %%

y_test_pred = model_pipe.predict(X_test)
y_test_prob = model_pipe.predict_proba(X_test)

acc_test = round(100*metrics.accuracy_score(y_test, y_test_pred),2)
roc_test = metrics.roc_auc_score(y_test, y_test_prob[:,1] )

print("Baseline: ", round((1-y_test.mean())*100,2))
print("acc_train:", acc_test)
print("roc_train:", roc_test)

# %%

skplt.metrics.plot_roc(y_test, y_test_prob)
plt.show()

# %%

skplt.metrics.plot_ks_statistic(y_test, y_test_prob)
plt.show()

# %%

skplt.metrics.plot_precision_recall(y_test, y_test_prob)
plt.show()

# %%

skplt.metrics.plot_lift_curve(y_test, y_test_prob)
plt.show()

# %%

features_model = model_pipe[:-1].transform(X_train.head()).columns.tolist()

fs_importance = pd.DataFrame({"importance":model_pipe[-1].feature_importances_,
                              "feature":features_model})

(fs_importance.sort_values("importance", ascending=False)
              .head(20))