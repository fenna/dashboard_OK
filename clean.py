#!/usr/bin/env python3

"""
This program reads a csv file and creates clean files for word analysis
"""

__author__ = "F.Feenstra"
__version__ = "0.1"


#import needed libraries to run this program
import sys
import pandas as pd

def clean_file(f):
    """
    function that preprocesses the file'
    -----
    input: f: filename
    output: df: dataframe (table)
    """
    df = pd.read_csv(f, delimiter = ';')
    print(df.columns.values.tolist())

    df['Zorgen']= df['Zorgen'].replace(-1, 'nee')
    df['Zorgen']= df['Zorgen'].replace(0, 'beetje')
    df['Zorgen']= df['Zorgen'].replace(1, 'ja')

    df['Eerlijk']= df['Eerlijk'].replace(-1, 'nee')
    df['Eerlijk']= df['Eerlijk'].replace(0, 'weet niet')
    df['Eerlijk']= df['Eerlijk'].replace(1, 'ja')

    df['Subsidies']= df['Subsidies'].replace(-1, 'nee')
    df['Subsidies']= df['Subsidies'].replace(0, 'weet niet')
    df['Subsidies']= df['Subsidies'].replace(1, 'ja')

    df = df.replace(-1, 6, regex=True) # -1 is set to 0 voor de stellingen
    df = df.replace(r'[^\sa-zA-Z0-9]+', "", regex=True) # troep eruit

    return df


def main():
    """ main function that calls the other functions"""
    file_to_process = input("geef de bestandsnaam op:")
    # try.csv veranderen in daadwerkelijke naam
    df = clean_file(file_to_process)
    # hier komt nog een regel dia alle NaN's eruit gooit
    # dit doen voor elke kolom die je wilt
    df['Zorgen.1'].dropna().to_csv('MD_clean_zorgen.csv')
    df['Eerlijk.1'].dropna().to_csv('MD_clean_eerlijk.csv')
    df['Subsidies.1'].dropna().to_csv('MD_clean_subsidies.csv')
    return 0


if __name__ == '__main__':
    sys.exit(main())
