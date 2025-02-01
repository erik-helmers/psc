from pathlib import Path
from functools import reduce
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt





class Indicators():

    def __init__(self, df_similar, df_non_similar, threshold):
        self.fp_len = len(df_non_similar)
        self.fn_len = len(df_similar)

        self.fp_count =  len(df_non_similar[df_non_similar['dist'] <= threshold])
        self.fn_count =  len(df_similar[df_similar['dist'] > threshold])

        self.tn_count = self.fp_len - self.fp_count
        self.tp_count = self.fn_len - self.fn_count

        self.fn_rate = self.fn_count / self.fn_len
        self.fp_rate = self.fp_count / self.fp_len

        self.global_precision = (self.tp_count + self.tn_count)/(self.tp_count + self.tn_count + self.fp_count + self.fn_count)

        if self.tp_count + self.fp_count != 0: precision = self.tp_count/(self.tp_count + self.fp_count)
        else: precision = 0
        self.precision = precision

        self.recall = self.tp_count/(self.tp_count + self.fn_count)


def intersection_fp_fn(fp: np.ndarray, fn: np.ndarray) -> np.ndarray:
        if fp.shape != fn.shape:
            raise ValueError("Les deux tableaux doivent avoir la même forme.")
        
        # Calculer la différence entre les deux fonctions
        difference = fp - fn
        
        # Trouver les indices où la différence change de signe
        intersection_indices = np.where(np.diff(np.sign(difference)))[0]
        
        return intersection_indices



def indicators_based_analysis_on_dfs(df_similar, df_non_similar, Plot=True):
    """Produces the ROC graph placed at an optimum threshold, calculated at the intersection of 
    FP rate and FN rate. bench_similar (resp. bench_non_similar) is the string name of a benchmark made of pairs of similar (resp. dissimilar) files.
    Returns the value of that optimal threshold and an Indicators() object at this threshold.
    """

    threshold_values = np.linspace(0, max(max(df_similar["dist"]), max(df_non_similar["dist"])), 200)
    fn_rate_values = np.array([Indicators(df_similar, df_non_similar, threshold).fn_rate for threshold in threshold_values])
    recall_values = np.array([Indicators(df_similar, df_non_similar, threshold).recall for threshold in threshold_values])
    fp_rate_values = np.array([Indicators(df_similar, df_non_similar, threshold).fp_rate for threshold in threshold_values])
    # Minimizing fp rate and fn rate to find an optimal value of threshold called here threshold_min
    
    index_min = intersection_fp_fn(fn_rate_values, fp_rate_values)[0]
    threshold_min = threshold_values[index_min]
    min_fp_fn = fn_rate_values[index_min]

    if Plot:
        # Printing FP and FN rate to find the intersection
        plt.close('all')
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].plot(threshold_values, fn_rate_values, color='yellow', label="FN rate")
        axes[0].plot(threshold_values, fp_rate_values, color='blue', label="FP rate")
        axes[0].axvline(x=threshold_min, color='r', linestyle='--', label=f'Seuil de travail = {threshold_min:.2f}')
        axes[0].axhline(y=min_fp_fn, color='r', linestyle='--')
        axes[0].scatter(threshold_min, min_fp_fn, color='red', zorder=5)  # Point de maximum
        axes[0].set_xlabel('Valeur du seuil')
        axes[0].set_ylabel('Pourcentage')
        axes[0].set_title("Définition du seuil de travail")
        axes[0].legend()
        
        # Courbe ROC
        axes[1].plot(fp_rate_values, recall_values)
        axes[1].set_xlabel("False positive rate")
        axes[1].set_ylabel("Recall")
        axes[1].set_title("Courbe ROC (Receiving Operating Characteristics)")
        
        plt.tight_layout()
        plt.show()
    return threshold_min, Indicators(df_similar, df_non_similar, threshold_min)
    
def algo_comparison_on_dfs(runners, benchmarks_similar, benchmarks_non_similar, Plot=True):

    thresholds = {}
    indicators = {}
    dataframes_similar = {}
    dataframes_non_similar = {}
    for runner in runners:
        dataframes_similar[runner] = np.array(benchmarks_similar[runner]["dist"])
        dataframes_non_similar[runner] = np.array(benchmarks_non_similar[runner]["dist"])
        threshold, indicator = indicators_based_analysis_on_dfs(benchmarks_similar[runner], benchmarks_non_similar[runner], Plot=False)
        thresholds[runner] = threshold
        indicators[runner] = indicator

    if Plot:
        plt.close('all')
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the fisrt algorithm outside of the loop to put the label
        ax.scatter([-0.1]*len(dataframes_similar[runners[0]]), dataframes_similar[runners[0]]/thresholds[runners[0]], label='Fichiers similaires', color='green', marker='o', s=5)  # Ronds
        ax.scatter([0.1]*len(dataframes_non_similar[runners[0]]), dataframes_non_similar[runners[0]]/thresholds[runners[0]], label='Fichiers non similaires', color='red', marker='s', s=5)  # Carrés

        # Tracer les points pour les deux séries
        for index, runner in enumerate(runners, start=1):
            ax.scatter([index-1.1]*len(dataframes_similar[runner]), dataframes_similar[runner]/thresholds[runner], color='green', marker='o', s=5)  # Ronds
            ax.scatter([index-0.9]*len(dataframes_non_similar[runner]), dataframes_non_similar[runner]/thresholds[runner], color='red', marker='s', s=5)  # Carrés

        # Horizontal line for the threshold
        ax.axhline(y=1, color='green', linestyle='--', linewidth=1.5, label='Seuil')

        # Axes and labels
        x = np.arange(len(runners))
        ax.set_xticks(x)
        ax.set_xticklabels(runners, rotation=45, ha='right')
        ax.set_xlabel('Algorithmes')
        ax.set_ylabel('Distances')
        ax.set_title('Distances renormalisées au seuil de travail par algorithme')

        ax.legend()

        plt.tight_layout()
        plt.show()

    return thresholds, indicators


def pretty(df):
    df['ref'] = df['ref'].apply(lambda x: Path(x).name)
    df['alt'] = df['alt'].apply(lambda x: Path(x).name)

    df = with_mods(df)
    df = suffix(df)
    df = wide(df)
    return df

def with_mods(df):
    df['mods'] = df['meta'].apply(lambda x: {
        k: x[k]  for k in x.keys() - {"ref", "alt", "dist"}})
    return df

def wide(df):
    base = reduce(lambda x, y: x|y, df['mods'], {})
    for param in base.keys():
        default = {int: 0, bool: False, str: ""}.get(type(base[param]))
        df[param] = df['mods'].apply(lambda x: x.get(param, default))
    return df

def long(df):
    base = reduce(lambda x, y: x|y, df['mods'], {})
    idx = df.columns.difference(base.keys())[::-1]
    df = df.melt(id_vars=idx, var_name="mod", value_name="modval")
    df = df.loc[df['modval']!=0, :]
    df['mod'] = df['mod'].astype('category')
    return df

def suffix(df):
    df['suffix'] = df['ref'].apply(lambda x: x.rsplit('.')[-1])
    return df



""" Compute the histogram of n-grams in the binary blob """
def ngrams(n, bytes_):
    out = np.zeros([256]*n, dtype=np.uint32)
    for i in range(len(bytes_)-n+1):
        out[tuple(bytes_[i:i+n])] += 1
    return out

