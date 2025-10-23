import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.cluster import KMeans
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import xgboost as xgb

warnings.filterwarnings('ignore')
RANDOM_STATE = 22
NUM_RANKS = 4
np.random.seed(RANDOM_STATE)

# Load player data
df = pd.read_csv("synthetic_player_data.csv")
print("Dataset shape:", df.shape)
print(df.head())

# Labeling method 1: Accuracy-based ranks
labels_acc = pd.qcut(df['accuracy'], q=NUM_RANKS, labels=False)
df['rank_acc_based'] = labels_acc + 1

# Labeling method 2: Cluster-based ranks
features_for_clustering = ['accuracy', 'avg_reaction_ms', 'shots_hit', 'shots_fired']
X_clust = df[features_for_clustering].copy()
scaler = StandardScaler()
X_clust_scaled = scaler.fit_transform(X_clust)

kmeans = KMeans(n_clusters=NUM_RANKS, random_state=RANDOM_STATE)
cluster_ids = kmeans.fit_predict(X_clust_scaled)

# Order clusters by accuracy to determine rank
cluster_order = (
    pd.DataFrame({'cluster': cluster_ids, 'accuracy': df['accuracy']})
    .groupby('cluster')
    .accuracy.mean()
    .sort_values()
    .index
    .tolist()
)
cluster_to_rank = {cluster_order[i]: i + 1 for i in range(NUM_RANKS)}
cluster_ranks = [cluster_to_rank[c] for c in cluster_ids]
df['rank_cluster_based'] = cluster_ranks

print('\nCluster means by accuracy:')
print(pd.DataFrame({'cluster': range(NUM_RANKS),
                    'mean_accuracy':
                    pd.DataFrame({'cluster': cluster_ids,'accuracy': df['accuracy']})
                    .groupby('cluster').accuracy.mean()}).sort_values('mean_accuracy'))

# Training 
def train_and_evaluate(df, label_col, drop_cols_for_training=None):
    df2 = df.copy()
    y = df2[label_col].astype(int) - 1  # 0..NUM_RANKS-1
    drop_cols = ['player_id','skill', label_col]
    if drop_cols_for_training:
        drop_cols += drop_cols_for_training
    feature_cols = [c for c in df2.columns if c not in drop_cols]
    X = df2[feature_cols].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=0.2, random_state=RANDOM_STATE
    )

    model = xgb.XGBClassifier(
        use_label_encoder=False, eval_metric='mlogloss',
        objective='multi:softprob', random_state=RANDOM_STATE,
        n_estimators=200, max_depth=4, learning_rate=0.1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Evaluation
    print(f"\n--- Trained XGBoost for label '{label_col}' ---")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification report:\n", classification_report(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix ({label_col})')
    plt.ylabel('True')
    plt.xlabel('Pred')
    plt.show()

    # Feature importance
    try:
        importance = model.get_booster().get_score(importance_type='gain')
        fi = {feature_cols[int(k[1:])]: v for k,v in importance.items()} if len(importance) else {}
    except Exception:
        fi = dict(zip(feature_cols, model.feature_importances_))
    fi_series = pd.Series(fi).sort_values(ascending=False)
    print("Top features by model importance:")
    print(fi_series.head(10))
    plt.figure(figsize=(8,4))
    sns.barplot(x=fi_series.values, y=fi_series.index)
    plt.title('Feature Importance (Gain)')
    plt.show()

    # Permutation importance
    try:
        print("Computing permutation importance...")
        r = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=RANDOM_STATE)
        perm_imp = pd.Series(r.importances_mean, index=feature_cols).sort_values(ascending=False)
        print("Top features by permutation importance:")
        print(perm_imp.head(10))
        plt.figure(figsize=(8,4))
        sns.barplot(x=perm_imp.values, y=perm_imp.index)
        plt.title('Permutation Feature Importance (Mean)')
        plt.show()
    except Exception as e:
        print("Permutation importance failed:", e)

    return model, feature_cols

# Run trainings
model_acc, feats_acc = train_and_evaluate(df, 'rank_acc_based', drop_cols_for_training=['accuracy','rank_cluster_based'])
model_clust, feats_clust = train_and_evaluate(df, 'rank_cluster_based', drop_cols_for_training=['rank_acc_based'])

# Example prediction for 1 player
example_row = df.loc[0, feats_clust].values.reshape(1, -1)
pred_cluster_rank = model_clust.predict(example_row)[0] + 1
print("\nExample predicted cluster-based rank for player 0:", pred_cluster_rank)
