# %%
import pandas as pd
import sqlalchemy

import matplotlib.pyplot as plt

from sklearn import model_selection
from sklearn import ensemble
from sklearn import tree
from sklearn import linear_model

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

rf_clf = ensemble.RandomForestClassifier(n_estimators=200,
                                         min_samples_leaf=20,                                        
                                         n_jobs=-1,
                                         random_state=42)

ada_clf = ensemble.AdaBoostClassifier(n_estimators=200,
                                      learning_rate=0.8,                                        
                                      random_state=42)

dt_clf = tree.DecisionTreeClassifier(max_depth=15,
                                     min_samples_leaf=50,
                                     random_state=42)

rl_clf = linear_model.LogisticRegressionCV(cv=4, n_jobs=-1)

## Definir um pipeline

params = {"n_estimators":[50,100,200,250],
          "min_samples_leaf": [5,10,20,50,100] }

grid_search = model_selection.GridSearchCV(rf_clf,
                                           params,
                                           n_jobs=1,
                                           cv=4,
                                           scoring='roc_auc',
                                           verbose=3,
                                           refit=True)

pipe_rf = pipeline.Pipeline(steps = [("Imput 0", imput_0),
                                     ("Imput -1", imput_1),
                                     ("One Hot", onehot),
                                     ("Modelo", grid_search)])


# %%
def train_test_report( model, X_train, y_train, X_test, y_test, key_metric, is_prob=True):
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)
    metric_result = key_metric(y_test, prob[:,1]) if is_prob else key_metric(y_test, pred)
    return metric_result

# %%

pipe_rf.fit(X_train, y_train)

# %%


## Assess
y_train_pred = pipe_rf.predict(X_train)
y_train_prob = pipe_rf.predict_proba(X_train)

acc_train = round(100*metrics.accuracy_score(y_train, y_train_pred),2)
roc_train = metrics.roc_auc_score(y_train, y_train_prob[:,1] )
print("acc_train:", acc_train)
print("roc_train:", roc_train)

# %%

print("Baseline: ", round((1-y_train.mean())*100,2))
print("Acurácia:", acc_train)

# %%

y_test_pred = pipe_rf.predict(X_test)
y_test_prob = pipe_rf.predict_proba(X_test)

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

skplt.metrics.plot_cumulative_gain(y_test, y_test_prob)
plt.show()


# %%

X_oot, y_oot = df_oot[features], df_oot[target]

y_prob_oot = pipe_rf.predict_proba(X_oot)

roc_oot = metrics.roc_auc_score(y_oot, y_prob_oot[:,1] )
print("roc_train:", roc_oot)

# %%
skplt.metrics.plot_lift_curve(y_oot, y_prob_oot)
plt.show()

# %%
skplt.metrics.plot_cumulative_gain(y_oot, y_prob_oot)
plt.show()


# %%

df_oot['prob'] = y_prob_oot[:,1]

# %%

conv_model = (df_oot.sort_values(by=['prob'], ascending=False)
                    .head(1000)
                    .mean()["prob"])

conv_sem = (df_oot.sort_values(by=['prob'], ascending=False)
                  .mean()["prob"])

total_model = (df_oot.sort_values(by=['prob'], ascending=False)
                     .head(1000)
                     .sum()["prob"])

total_sem = (df_oot.sort_values(by=['prob'], ascending=False)
                   .sum()["prob"])


print(f"Total convertidos modelo {total_model} ({round(100*conv_model,2)}%)")
print(f"Total convertidos SEM modelo {total_sem} ({round(100*conv_sem,2)}%)")