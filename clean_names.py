import os
import glob
import pandas as pd
path = "/Users/Dani/Dropbox/Muni_Finance_Lab/Raw_Data/Appeals"


def add_clean_name(df, file):
    try:
        df['clean_name']
        print "Clean column already exists in file " + file[54:]

    except KeyError:
        df["clean_name"] = df["attorneytaxrep"].str.replace("\.|\s|,", "")
        print "FINISHED cleaning lawyer names for file " + file[54:]

    return df

if __name__=="__main__":

    files = glob.glob(path + "/*.csv")

    assert len(files) == 13

    for f in files:
        df = pd.read_csv(f,index_col=None, header=0)
        df = add_clean_name(df, f)
        df.to_csv(path + f[54:])