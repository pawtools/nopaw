#!/usr/bin/env python

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..logger import get_logger

logger = get_logger(__name__)

__all__ = [
    "makeplot",
]

# FIXME TODO point-source config and thne late binding
#            ie get rid of globals here and get from rc file

# CHANGE these wherever to alter
#        plot appearance
lw_plot = 2.5
lw_axis = 3.5
lw_ticks = 2.5
fs_title = 22
fs_axlabel = 19
fs_tklabel = 15
rot_tklabel = 45


def scaling_plot(plt, X, Y, xlim, ylim, xlabel, ylabel, title, filename):
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    ax.plot(X, Y, linewidth=lw_plot)
    ax.scatter(X, Y, marker='s')
    format_plot(plt, ax, xlim, ylim, xlabel, ylabel, title, filename)


def format_plot(plt, ax, xlim, ylim, xlabel, ylabel, title, filename):
    #ax.set_xscale('log')
    ax.set_xlabel(xlabel, fontsize=fs_axlabel)
    ax.set_ylabel(ylabel, fontsize=fs_axlabel)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_title(title, fontsize=fs_title)
    ax.xaxis.set_tick_params(width=lw_ticks)
    ax.yaxis.set_tick_params(width=lw_ticks)

    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(lw_axis)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(fs_tklabel)
        #tick.label.set_rotation(rot_tklabel)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(fs_tklabel)
        #tick.label.set_rotation(rot_tklabel)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def makeplot(X, Y, plot_filename, config=None):

    xmax = np.max(X)
    xlim = [0, xmax + 0.05 * xmax]

    if config is None:

        xlabel = "N Task Replicates"
        ylabel = "Workload Duration (seconds)"
        title = "Weak Scaling of Workload Duration"
        legend_labels = list()

    elif isinstance(config, dict):
        pass

    elif os.path.exists(config):
        pass

    if isinstance(Y, (tuple,list)):
        ymax = np.max(Y)
        ylim = [0, ymax  + 0.05 * ymax]

    elif isinstance(Y, np.ndarray):
        ymax = np.max(Y)
        ylim = [0, ymax  + 0.05 * ymax]

    elif isinstance(Y, dict):

        if len(Y) == 1:
            ylabel, Y = Y.items()[0]
            ymax = np.max(Y)
            ylim = [0, ymax  + 0.05 * ymax]

        else:
            pass # keys as legend labels

    else:
        logger.warning("Could not understand what Y was: {}".format(Y))
        raise Exception

    scaling_plot(plt, X, Y, xlim, ylim, xlabel, ylabel, title, plot_filename)

