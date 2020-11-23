# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from db import *
import excel as ex
import sql
import datacleaner as dc

# Press the green button in the gutter to run the script.
file = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\PVLDBDB\2020-07-09-PVLDB-Members.xlsx"


# write csv to db
def write_journal_to_db(csv, dbConnection, journalVol):
    df = ex.read_csv(csv)
    for index, row in df.iterrows():
        print(row['FirstName'], row['LastName'], row['Role'])
        dbConnection.insert_journal_res_entry(row['FirstName'], row['LastName'], row['OrcID'],
                                              row['Affiliation'], row['Location'], row['Country'], journalVol, row['Role'])


# basi cleaning
def init_run(journalVol):
    fileNumber = 14 - journalVol
    # basic separation of the string in name and affiliation
    df = dc.sort_excel(file, fileNumber, "sep")

    # basic replacement of strings
    df = dc.preclean(df)
    # separates the affiliation string
    df = dc.sort_affiliation_string(df)
    # correct affiliations by substituting
    df = dc.correct_affiliations(df)
    # separates the affiliation string
    df = dc.sort_affiliation_string(df)
    # add affiliations if missing
    df = dc.fill_affiliation_from_db(df)
    print(df.to_string())
    ex.write_csv(df, 'VLDB{}'.format(journalVol))


# manual sorting
def first_run(journalVol):
    # read as dataframe
    df = ex.read_csv('VLDB{}'.format(journalVol))
    # compare affiliation with db
    dc.compare_affiliation_with_db(df)


# automated adding from db
def second_run(journalVol):
    # read as dataframe
    df = ex.read_csv('VLDB{}'.format(journalVol))
    # add stuff from db
    df = dc.fill_affiliation_from_db(df)
    df = dc.fill_country_from_db(df)
    # write csv
    ex.write_csv(df, 'VLDB{}'.format(journalVol))


# add orcid
def third_run(journalVol):
    # add orcid to dataframe
    df = dc.add_orcid(journalVol)


# write csv to db
def write_to_db():
    db = DB("sqlite")
    db.reset()
    for i in range(14, 10, -1):
        write_journal_to_db('VLDB{}'.format(i), db, i)


if __name__ == '__main__':
    journalVol = 7
    #init_run(journalVol)
    # first_run(journalVol)
    # second_run(journalVol)
    # third_run(journalVol)

    write_to_db()

    # sql queries
    # print(sql.get_journal(journalVol))

    # country statistics
    # df2 = get_country_stat()
    # ex.write_csv(df2, 'country_stat')
    # print(df2)
