# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import pandas as pd
import db
import excel as ex

# Press the green button in the gutter to run the script.

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


def getCountry():
    return pd.read_sql(db.countrySQL, con=db.mydb)


def getJournal(journalVol):
    return pd.read_sql(db.journalSQL % journalVol, con=db.mydb)


if __name__ == '__main__':
    #filestring = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\2020-07-09-PVLDB-Members.xlsx"
    #sort_excel(filestring, 0, 'VLDB14')
    #csv = r"csv\VLDB13.csv"
    #df = read_csv(csv)
    #df = df.replace({np.nan: None})
    #print(df.to_string())
    #reset()
    #for index, row in df.iterrows():
    #    insert_journal_entry(row['FirstName'], row['LastName'], row['OrcID'],
    #                               row['Affiliation'], row['Country'], 13, row['Role'])
    #print(get_by_country())

    #check_person("Wolfgang", "Lehner")
    df2 = getCountry()
    ex.write_csv(df2, 'country_stat')
    print(df2)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
