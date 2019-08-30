import numpy as np
import matplotlib as mpl
_ = mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math
import os
import pickle
from matplotlib.patches import Rectangle

def adv_table_helper(df, annot_nn, md, data, folder, norms=False):
    # vmin = math.floor(df.values.min())
    # vmin = df.values.min()
    vmin = 0.0
    # vmax = math.ceil(df.values.max())
    vmax = df.values.max()
    seqlen = data['emb_cos_nn'].size

    size_h = seqlen / 4.0
    size_w = 8

    fig = plt.figure(figsize=(size_w, size_h))
    if norms:
        main_plot = sns.heatmap(df, annot=True, fmt='.3f', cmap='YlOrRd', vmin=vmin, vmax=vmax, cbar=False)
        # main_plot = sns.heatmap(df, annot=True, fmt='.3f', cmap='YlOrRd', vmin=vmin, vmax=vmax)
    else:
        main_plot = sns.heatmap(df, annot=annot_nn, fmt='', cmap='YlOrRd', vmin=vmin, vmax=vmax, cbar=False)
        # main_plot = sns.heatmap(df, annot=annot_nn, fmt='', cmap='YlOrRd', vmin=vmin, vmax=vmax)
    main_plot.set_xticklabels(main_plot.get_xticklabels(), rotation=0)

    sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=mpl.colors.Normalize(vmin=vmin,vmax=vmax))
    cbaxes = fig.add_axes([0.97, 0.1, 0.03, 0.8])
    sm.set_array([])
    cb = plt.colorbar(sm ,cbaxes)

    ax2 = main_plot.twinx()
    ax2.set_ylim((-0.5,seqlen-0.5))
    ax2.set_yticks(np.arange(0.0,seqlen,1.0))
    ax2.invert_yaxis()
    ax2.set_yticklabels(np.around(data['cos_emb_adv'], 3))

    if norms:
        plt.title(r'Norms, $\epsilon = $' + md['adv_k'] + 'x' + md['epsilon'] + ' ' + md['label'])
        plt.savefig(os.path.join(folder, md['name'] + '_adv_k' + md['adv_k'] + '_eps' + md['epsilon'] + '_norms.png'), bbox_inches='tight')
    else:
        plt.title(r'Nearest neighbors, $\epsilon = $' + md['adv_k'] + 'x' + md['epsilon'] + ' ' + md['label'])
        plt.savefig(os.path.join(folder, md['name'] + '_adv_k' + md['adv_k'] + '_eps' + md['epsilon'] + '_nns.png'), bbox_inches='tight')
    plt.clf()

def create_adv_table(data, metadata, folder='temp', save_norms=True):
    # General stuff
    md = metadata
    annot_nn = np.stack([data['emb_cos_nn'], data['per_cos_nn'], data['adv_cos_nn']], axis=1)
    df = pd.DataFrame({'original': data['emb_l2_norm'], 'perturbation': data['per_l2_norm'], 'adversarial': data['adv_l2_norm']},
        index=np.arange(data['emb_l2_norm'].size))
    df = df[['original', 'perturbation', 'adversarial']]

    adv_table_helper(df, annot_nn, md, data, folder)
    adv_table_helper(df, annot_nn, md, data, folder, save_norms)

def summary_histogram(measure, cosnn_meas, random_meas, eucnn_meas, density=True, folder='temp', suffix=''):

    if suffix != '':
        suffix = '_' + str(suffix)

    if measure is 'cosine':
        meas_bins = np.arange(0.0, 1.02, 0.02)
        meas_xlabel = 'Cosine similarity'

    elif measure is 'euclidean':
        bare_max = np.max([np.max(random_eucs), np.max(eucnn_eucs[:, 1:]), np.max(cosnn_eucs[:, 1:])])
        set_max = np.round(bare_max * 1.01, 2)
        step = set_max / 50
        meas_bins = np.arange(0.0, set_max + step, step)
        meas_xlabel = 'Euclidean (L2) distance'

    cosnn_meas_org = cosnn_meas[:,:]
    random_meas = random_meas.flatten()
    cosnn_meas = cosnn_meas[:, 1:].flatten()
    eucnn_meas = eucnn_meas[:, 1:].flatten()

    random_counts, bins = np.histogram(random_meas, meas_bins)
    cosnn_counts, bins = np.histogram(cosnn_meas, meas_bins)
    eucnn_counts, bins = np.histogram(eucnn_meas, meas_bins)
    if density:
        random_counts = random_counts / random_meas.size
        cosnn_counts = cosnn_counts / cosnn_meas.size
        eucnn_counts = eucnn_counts / eucnn_meas.size

    ymax = np.max([np.max(random_counts), np.max(cosnn_counts), np.max(eucnn_counts)])

    plt.hist(meas_bins[:-1], meas_bins, weights=random_counts, facecolor='r', alpha=0.50)
    plt.hist(meas_bins[:-1], meas_bins, weights=cosnn_counts, facecolor='g', alpha=0.50)
    plt.hist(meas_bins[:-1], meas_bins, weights=eucnn_counts, facecolor='b', alpha=0.50)
    handles = [Rectangle((0,0), 1, 1, color=c, ec='k') for c in ['r', 'g', 'b']]
    labels = ['random', 'cosnn', 'eucnn']
    plt.legend(handles, labels)
    plt.xlabel(meas_xlabel)
    plt.ylabel('Probability')
    plt.title('Summary histogram')
    plt.grid(True)
    plt.ylim((0, ymax * 1.02))
    plt.savefig(os.path.join(folder, measure + str(suffix) + '.png'), bbox_inches='tight')
    plt.clf()

    plot_array = [
                ('Random sampling', 'random', random_counts, 'r'),
                ('Cosine nearest neighbors', 'cosnn', cosnn_counts, 'g'),
                ('Euclidean nearest neighbors', 'eucnn', eucnn_counts, 'b')]
    for (title, name, data, color) in plot_array:
        plt.hist(meas_bins[:-1], meas_bins, weights=data, facecolor=color)
        plt.xlabel(meas_xlabel)
        plt.ylabel('Probability')
        plt.title(title)
        plt.grid(True)
        plt.ylim((0, ymax * 1.02))
        plt.savefig(os.path.join(folder, measure + '_' + name + str(suffix) + '.png'), bbox_inches='tight')
        plt.clf()

if __name__ == "__main__":

    # pik_file = 'example_adv_data.pickle'
    # with open(os.path.join('./', pik_file), 'rb') as handle:
    #     data = pickle.load(handle)
    #     metadata = pickle.load(handle)
    # metadata['name'] = 'example'
    # create_adv_table(data, metadata, folder='out_imdb', save_norms=True)

    pik_file = 'summary_data_10000_5_5.pickle'
    with open(os.path.join('./', pik_file), 'rb') as handle:
        random_cosines = pickle.load(handle)
        random_eucs = pickle.load(handle)
        cosnn_cosines = pickle.load(handle)
        eucnn_eucs = pickle.load(handle)
        eucnn_cosines = pickle.load(handle)
        cosnn_eucs = pickle.load(handle)

    summary_histogram('cosine', cosnn_cosines, random_cosines, eucnn_cosines, density=True, folder='out_imdb')
    summary_histogram('euclidean', cosnn_eucs, random_eucs, eucnn_eucs, density=True, folder='out_imdb')
