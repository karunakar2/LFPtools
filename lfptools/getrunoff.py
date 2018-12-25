#!/usr/bin/env python

# inst: university of bristol
# auth: jeison sosa
# mail: j.sosa@bristol.ac.uk / sosa.jeison@gmail.com

import sys
import getopt
import configparser
import numpy as np
import pandas as pd


def getrunoff(argv):

    opts, args = getopt.getopt(argv, "i:")
    for o, a in opts:
        if o == "-i":
            inifile = a
    config = configparser.SafeConfigParser()
    config.read(inifile)

    discsv = str(config.get('getrunoff', 'discsv'))
    output = str(config.get('getrunoff', 'output'))

    print("    running getrunoff.py...")

    # Reading discharge data
    df = pd.read_csv(discsv, index_col=0)

    # Use discharge CSV to calculate runoff
    grouped = df.groupby('link')
    res = pd.DataFrame()
    for name, group in grouped:
        # Select only date columns
        diffgroups = group[[i for i in df.columns if i[0] == '1']].diff()
        res = pd.concat([res, diffgroups])
    df1 = pd.concat([df[['link', 'x', 'y', 'near_x', 'near_y']], res], axis=1)

    # Remove NANs from all rows + change negative values by NANs + filling NANs by interpolation per 'linkno'
    df1.dropna(inplace=True)
    df1[df1[[i for i in df1.columns if i[0] == '1']]
        < 0] = np.nan  # Select only date columns
    df1 = df1.groupby('link').apply(lambda grp: grp.interpolate(
        method='linear', limit_direction='both'))
    df1[df1.isnull()] = 0

    # Writing CSV file
    df1.to_csv(output)


if __name__ == '__main__':
    getrunoff(sys.argv[1:])
