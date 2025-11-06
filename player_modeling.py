import os
import sys
import argparse
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score
)

# ---------- Configuration ----------
RANDOM_STATE = 22
SEED = RANDOM_STATE
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
DATA_PATH = "player_data.csv"

# ---------- Utilities ----------

def savefig(fig, name: str, dpi: int = 150):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=dpi)
    print(f"Saved: {path}")


def ensure_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe containing only numeric columns (drops non-numeric).
    Also prints which columns were dropped for transparency.
    """
    non_num = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_num:
        print("Dropping non-numeric columns:", non_num)
    return df.select_dtypes(include=["number"]).copy()


# ---------- Load & Clean ----------

def load_and_clean(path: str = DATA_PATH) -> pd.DataFrame:
    """Load CSV, attempt to standardize column names, drop PlayerID/timestamp if present.
    Returns a cleaned numeric-only DataFrame.
    """
    print("Loading:", path)
    df = pd.read_csv(path)
    print("Raw columns:", list(df.columns))

    df.columns = [c.strip().replace(" ", "_").replace("\t", "_") for c in df.columns]

   

    drop_cols = ['PlayerID', 'Timestamp']
    for col in drop_cols:
        print("Dropping columns:", col)
        df = df.drop(columns=col, errors="ignore")


    df = ensure_numeric_df(df)

    print("Cleaned dataframe shape:", df.shape)
    print(df.dtypes)
    return df


# ---------- Gap statistic (Tibshirani) ----------

def gap_statistic(X: np.ndarray, refs: int = 10, ks: range = range(1, 11), random_state: int = SEED) -> Tuple[np.ndarray, np.ndarray, int]:
    rng = np.random.RandomState(random_state)
    shape = X.shape
    tops = X.max(axis=0)
    bots = X.min(axis=0)

    gaps = []
    s_k = []
    for k in ks:
        ref_inertias = []
        for i in range(refs):
            X_ref = rng.rand(shape[0], shape[1]) * (tops - bots) + bots
            km = KMeans(n_clusters=max(1, k), n_init=10, random_state=random_state)
            km.fit(X_ref)
            ref_inertias.append(km.inertia_)
        km = KMeans(n_clusters=max(1, k), n_init=10, random_state=random_state)
        km.fit(X)
        orig_inertia = km.inertia_
        log_refs = np.log(ref_inertias)
        gap = np.mean(log_refs) - np.log(orig_inertia)
        sk = np.sqrt(np.mean((log_refs - log_refs.mean()) ** 2)) * np.sqrt(1.0 + 1.0 / refs)
        gaps.append(gap)
        s_k.append(sk)

    optimal_k = None
    ks_list = list(ks)
    for i in range(len(ks_list) - 1):
        if gaps[i] >= gaps[i + 1] - s_k[i + 1]:
            optimal_k = ks_list[i]
            break
    if optimal_k is None:
        optimal_k = ks_list[-1]
    return np.array(gaps), np.array(s_k), optimal_k


# ---------- Evaluate k options ----------

def evaluate_k_options(X: np.ndarray, k_min: int = 2, k_max: int = 8, random_state: int = SEED) -> Dict:
    ks = list(range(k_min, k_max + 1))
    inertias = []
    sil_scores = []
    ch_scores = []
    db_scores = []

    for k in ks:
        km = KMeans(n_clusters=k, n_init=20, random_state=random_state)
        labels = km.fit_predict(X)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X, labels) if k > 1 else np.nan)
        ch_scores.append(calinski_harabasz_score(X, labels))
        db_scores.append(davies_bouldin_score(X, labels))

    gaps, sk, gap_k = gap_statistic(X, refs=10, ks=range(1, k_max + 1), random_state=random_state)

    # plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.ravel()
    axes[0].plot(ks, inertias, marker="o")
    axes[0].set_title("Inertia (Elbow)")
    axes[0].set_xlabel("k")

    axes[1].plot(ks, sil_scores, marker="o")
    axes[1].set_title("Silhouette")

    axes[2].plot(ks, ch_scores, marker="o")
    axes[2].set_title("Calinski-Harabasz")

    axes[3].plot(ks, db_scores, marker="o")
    axes[3].set_title("Davies-Bouldin (lower better)")

    plt.tight_layout()
    savefig(fig, "k_evaluation.png")
    plt.show()

    print("Inertia:", inertias)
    print("Silhouette:", sil_scores)
    print("Gap suggests k:", gap_k)
    print("Best silhouette k:", ks[int(np.nanargmax(sil_scores))])

    return {
        "ks": ks,
        "inertia": inertias,
        "silhouette": sil_scores,
        "calinski_harabasz": ch_scores,
        "davies_bouldin": db_scores,
        "gap": (gaps, sk, gap_k),
    }


# ---------- Full dataset clustering ----------

def cluster_full(df: pd.DataFrame, k: int = 2):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)

    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE)
    labels = km.fit_predict(X_scaled)
    df_out = df.copy()
    df_out["cluster"] = labels

    print("Cluster means:")
    cluster_means = df_out.groupby("cluster").mean()
    print(cluster_means)
    centroids_df = cluster_means.reset_index()
    centroids_file = os.path.join(OUTPUT_DIR, f"full_clusters_k{k}_centroids.csv")
    centroids_df.to_csv(centroids_file, index=False)
    print(f"Saved full cluster centroids: {centroids_file}")

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X_scaled)
    df_out["pc1"] = coords[:, 0]
    df_out["pc2"] = coords[:, 1]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x="pc1", y="pc2", hue="cluster", data=df_out, palette="deep", ax=ax)
    ax.set_title(f"Full-dataset clusters (k={k}) PCA")
    savefig(fig, f"full_clusters_k{k}.png")
    plt.show()

    return df_out, km, scaler, pca


# ---------- Subset clustering ----------

def cluster_subset(df: pd.DataFrame, features: List[str], k: int = 3) -> Tuple[pd.DataFrame, KMeans, StandardScaler]:
    assert all(f in df.columns for f in features), "Some features not in df"
    df_sub = df[features].copy()
    scaler = StandardScaler()
    Xs = scaler.fit_transform(df_sub)

    km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE)
    labels = km.fit_predict(Xs)
    out = df_sub.copy()
    out["cluster"] = labels

    print(f"Cluster means for features={features} (k={k}):")
    cluster_means = out.groupby("cluster").mean()
    print(cluster_means)

    centroids_df = cluster_means.reset_index()
    centroids_file = os.path.join(OUTPUT_DIR, f"subset_{'_'.join(features)}_k{k}_centroids.csv")
    centroids_df.to_csv(centroids_file, index=False)
    print(f"Saved subset cluster centroids: {centroids_file}")

    if len(features) == 2:
        fig, ax = plt.subplots(figsize=(7, 6))
        sns.scatterplot(x=features[0], y=features[1], hue="cluster", data=out, palette="deep", ax=ax)
        ax.set_title(f"Subset clustering: {features} (k={k})")
        savefig(fig, f"subset_{features[0]}_{features[1]}_k{k}.png")
        plt.show()

    else:
        pca = PCA(n_components=2, random_state=RANDOM_STATE)
        coords = pca.fit_transform(Xs)
        out["pc1"] = coords[:, 0]
        out["pc2"] = coords[:, 1]
        fig, ax = plt.subplots(figsize=(7, 6))
        sns.scatterplot(x="pc1", y="pc2", hue="cluster", data=out, palette="deep", ax=ax)
        ax.set_title(f"Subset clustering PCA: {features} (k={k})")
        savefig(fig, f"subset_{'_'.join(features)}_k{k}.png")
        plt.show()

    return out, km, scaler


# ---------- PCA analysis ----------

def pca_analysis(df: pd.DataFrame, n_components: int = 5):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(df)
    pca = PCA(n_components=n_components, random_state=RANDOM_STATE)
    pca.fit(Xs)

    explained = pca.explained_variance_ratio_
    print("Explained variance ratio:", explained)
    loadings = pd.DataFrame(pca.components_.T, index=df.columns, columns=[f"PC{i+1}" for i in range(n_components)])
    print("Top loadings:")
    print(loadings.abs().sort_values(by="PC1", ascending=False).head(10))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(1, n_components + 1), explained)
    ax.set_xlabel("PC")
    ax.set_ylabel("Explained variance ratio")
    ax.set_title("PCA explained variance")
    savefig(fig, "pca_explained_variance.png")
    plt.show()

    return pca, loadings


# ---------- CLI / Interactive ----------

def interactive_menu(data_path: str = DATA_PATH):
    df = load_and_clean(data_path)

    while True:
        print("\n--- Menu ---")
        print("1) Evaluate k options (elbow/silhouette/CH/DB/gap)")
        print("2) Run full-dataset clustering (choose k)")
        print("3) Run subset clustering (choose features & k)")
        print("4) PCA analysis")
        print("0) Exit")

        choice = input("Choose: ")
        if choice == "1":
            X = StandardScaler().fit_transform(df)
            evaluate_k_options(X, k_min=2, k_max=8)
        elif choice == "2":
            k = int(input("k (e.g. 2 or 4): "))
        elif choice == "3":
            feats = input("Comma-separated features (exact column names): ").split(",")
            feats = [f.strip() for f in feats]
            k = int(input("k for subset: "))
            cluster_subset(df, feats, k=k)
        elif choice == "4":
            pca_analysis(df, n_components=6)

        elif choice == "0":
            print("Exit")
            break
        else:
            print("Unknown choice")


# ---------- Run as script ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Player modeling clustering pipeline")
    parser.add_argument("--data", type=str, default=DATA_PATH, help="Path to CSV data")
    args = parser.parse_args()
    if not os.path.exists(args.data):
        print(f"Data file not found: {args.data}")
        print("Please place your CSV at this path or pass --data path/to/file.csv")
        sys.exit(1)

    interactive_menu(args.data)

