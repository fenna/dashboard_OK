#!/usr/bin/env python3

"""
This program searches for csv files in the project directory and creates plots
"""

__author__ = "F.Feenstra"
__version__ = "0.4"


#import needed libraries to run this program
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import pydoc
import yaml


CATEGORY_NAMES = { 0: 'onbekend',
                   1: 'helemaal oneens',
                   2: 'oneens',
                   3: 'nog oneens nog eens',
                   4: 'eens',
                   5: 'helemaal mee eens',
                   6: '?'}

def clean_file(f):
    """
    function that extracts only the 7 columns of the stellingen and
    preprocess the values
    -----
    input: f: filename
    output: df: dataframe (table)
    """
    df = pd.read_csv(f, delimiter = ';')
    df = df.replace(r'^\s*$', 0, regex=True) #spaces are set to 0
    df = df.replace(-1, 6, regex=True) # -1 is set to 6 (weet niet)
    # colums aanpassen
    df = df[['1','2','3','4','5','6','7']] # use only the stellingen column
    return df


def setlabels(df):
    """
    Function that fills an array with 'stellingen' from the configfile
    """
    # read the config file
    file = open('config.yml', 'r')
    cfg = yaml.load(file, Loader=yaml.FullLoader)
    # create an array questions from configfile
    questions =[(cfg['stellingen'][i]) for i in range(1, 8)]
    return questions


def fill_array(df, colno):
    """
    Function to fill an array y with the numbers of occurrence per category
    it uses parameters:
    --------
    df: dataframe from file
    colno: collumno of the dataframe (usally a survey question)
    y: an array with all the counts per outcome in percentage
    """
    # get all the values from a column
    x = np.array(np.array(df.iloc[:,[colno]].dropna().astype(int)))
    # get unique answers and amount per unique answers
    unique_elements, counts_elements = np.unique(x, return_counts=True)
    # compose array with amount per answer
    y = np.array([0,0,0,0,0,0,0])
    for idx, i in enumerate(unique_elements):
        y[i] = counts_elements[idx]
    y_perc = np.array([i/y.sum()*100 for i in y])
    return y_perc


def survey(results, category_names):
    """
    This funtion creates the graph. It uses the following parameters:
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.1, 1.13, data.shape[1]))

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        if i == 5 :  # display bars with 'weet niet'
            ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color='grey')
            xcenters = starts + widths / 2
        else:
            ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color=color) # color is red to green
            xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c != 0:
                ax.text(x, y, str(int(c)), ha='center', va='center',color=text_color)

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),loc='lower left', fontsize='small')
    return fig, ax


def main(args):
    """ main function that calls all the other functions"""
    try:
        if len(args) == 1:
            # get all the csv files that are in the current directory
            files = [os.path.basename(x) for x in glob.glob("*.csv")]
        else:
            files = args[1:]
        # create a figure for each file
        for f in files:
           df = clean_file(f)
           questions = setlabels(df)
           results = {questions[i] : fill_array(df, i)[1:] for i in range(0, 7)}
           category_names = [CATEGORY_NAMES[i] for i in CATEGORY_NAMES][1:]
           fig, ax = survey(results, category_names)
           plt.tight_layout()
           plt.savefig(f[:-4])
    #except:
        # print documentation in case of error
        # print(pydoc.help(__name__))
    finally:
        print(f"programma heeft {len(files)} figuren gemaakt van bestanden: {files}")

    return 0


if __name__ == "__main__":
    exitcode = main(sys.argv)
    sys.exit(exitcode)
