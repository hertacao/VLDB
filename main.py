# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import pandas as pd
from sql import *
import excel as ex
from db_conncet import *

# Press the green button in the gutter to run the script.
file = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\2020-07-09-PVLDB-Members.xlsx"


def sort_excel(filestring, sheet, csv):
    df = ex.read_excel(filestring, sheet)
    df.insert(1, 'FirstName', [ex.get_firstname(name) for name in df['Name']])
    df.insert(2, 'LastName', [ex.get_lastname(name) for name in df['Name']])
    print("names inserted")
    df['OrcID'] = [ex.search_orcid(name) for name in df['Name']]

    print(df.to_string())
    ex.write_csv(df, csv)


def sort_excel_messy(filestring, sheet, csv):
    df = ex.read_excel(filestring, sheet)
    df.insert(1, 'FirstName', [ex.get_firstname(ex.get_name(string)) for string in df['Name']])
    df.insert(2, 'LastName', [ex.get_lastname(ex.get_name(string)) for string in df['Name']])
    print("names inserted")
    df['Affiliation'] = [ex.get_affiliation(string) for string in df['Name']]
    print("affiliation inserted")
    df['OrcID'] = [ex.search_orcid(name) for name in df['Name']]

    print(df.to_string())
    ex.write_csv(df, csv)


def getCountryStat():
    return pd.read_sql(countrySQL, con=mydb)


def getJournal(journalVol):
    return pd.read_sql(journalSQL % journalVol, con=mydb)


def writeJournalToDB(csvString, dbConnection, journalVol):
    df = ex.read_csv(csvString)
    df = df.replace({np.nan: None})
    for index, row in df.iterrows():
        dbConnection.insert_journal_res_entry(row['FirstName'], row['LastName'], row['OrcID'],
                                              row['Affiliation'], row['Country'], journalVol, row['Role'])


if __name__ == '__main__':
    # sort_excel(filestring, 0, 'VLDB14')
    csv = r"csv\VLDB13.csv"
    db = DB(mydb)
    db.reset()
    writeJournalToDB(csv, db, 13)
    print(getJournal(13))

    # df2 = getCountryStat()
    # ex.write_csv(df2, 'country_stat')
    # print(df2)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
