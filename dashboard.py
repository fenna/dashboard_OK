#!/usr/bin/env python3

"""
This program searches for csv files in the project directory and creates plots
"""

__author__ = "F.Feenstra"
__version__ = "0.3"


#import needed libraries to run this program
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import pydoc
import yaml


def fill_array(df, colno):
    """ 
    Function to fill an array y with the numbers of occurrence per category
    it uses parameters:
    --------
    df: dataframe from file
    colno: collumno of the dataframe (usally a survey question)
    """
    # get all the values from a column, drop the empty ones
    x = np.array(np.array(df.iloc[:,[colno]].dropna().astype(int)))
    # initialize empty array for counts ['weet niet', 'helemaal oneens' ...'helemaal mee eens']
    y = np.array([0,0,0,0,0,0]) 
    # get unique answers and amount per unique answers
    unique_elements, counts_elements = np.unique(x, return_counts=True)
    # compose array with amount per answer
    for idx, i in enumerate(unique_elements):
        y[i] = counts_elements[idx]
    # count all the non 1 - 5 to 'weet niet'
    if sum(counts_elements) != len(df.index):
        y[0] = len(df.index) - (sum(counts_elements[1:]))
    return y


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
    
    category_colors = plt.get_cmap('RdYlGn')(
        # start color of 'helemaal oneens', end color 'helemaal eens'
        np.linspace(-0.1, 0.9, data.shape[1])) 

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        # display bars with 'weet niet'
        if i == 0:
            # need thicker axes? adap height
            ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color='grey')
            xcenters = starts + widths / 2
        # display bars with ''helemaal oneens', 'oneens','nog oneens nog eens', 'eens', 'helemaal mee eens''  
        else:
            # need thicker axes? adap height
            ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color=color) # color is red to green
            xcenters = starts + widths / 2

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c != 0:
                ax.text(x, y, str(int(c)), ha='center', va='center',color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    return fig, ax


def clean_file(f):
    """ 
    function that cleans all the file and set unknown to 0 = 'weet niet' 
    -----
    input: f: filename
    output: df: dataframe (table)
    """
    df = pd.read_csv(f, delimiter = ';')
    df = df.replace(r'^\s*$', 0, regex=True) #spaces are set to 0 (weet niet)
    df = df.replace(-1, 0, regex=True) # -1 is set to 0 (weet niet)
    return df


def question_setlabels(df):
    """ 
    Function that fills an array with collumnames and replaces the 
    columname 7 .. 14 with 'stellingen' from the configfile
    ------
    dfcolumns.values.tolist(): list with table headers
    questions: table with tableheaders and 'stellingen' (instead of 1..7)
    """
    questions = df.columns.values.tolist()
    file = open('config.yml', 'r')
    cfg = yaml.load(file, Loader=yaml.FullLoader)
    # stellingen starts at column number 7
    for i in range(7, 14):
        questions[i] = (cfg['stellingen'][i-6])
    return questions


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
           questions = question_setlabels(df)
           category_names = ['?','helemaal oneens', 'oneens',
              'nog oneens nog eens', 'eens', 'helemaal mee eens']
           results = {questions[i] : fill_array(df, i) for i in range(7, 14)}
           fig, ax = survey(results, category_names)
           plt.tight_layout()
           plt.savefig(f[:-4])
    except:
        # print documentation in case of error
        print(pydoc.help(__name__))
    finally:
        print(f"programma heeft {len(files)} figuren gemaakt van bestanden: {files}")

    return 0


if __name__ == "__main__":
    exitcode = main(sys.argv)
    sys.exit(exitcode)










