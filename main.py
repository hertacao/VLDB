# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from db import *
import db as db
import excel as ex
import sql
import datacleaner as dc

# Press the green button in the gutter to run the script.
file = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\PVLDBDB\2020-07-09-PVLDB-Members.xlsx"
conf_file = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\PVLDBDB\VLDB Conferences.xlsx"
conf_role = r"C:\Users\herta\OneDrive\Dokumente\Arbeit\PVLDBDB\PVLDBDB Tables.xlsx"


# write csv to db
def write_journal_to_db(csv, dbConnection, journalVol):
    df = ex.read_csv(csv)
    for index, row in df.iterrows():
        print(row['FirstName'], row['LastName'], row['Role'])
        dbConnection.insert_journal_res_entry(row['FirstName'], row['LastName'], row['OrcID'],
                                              row['Affiliation'], row['Location'], row['Country'], journalVol,
                                              row['Role'])


def write_conf_to_db(csv, dbConnection, confYear):
    df = ex.read_csv(csv)
    confRoles = ex.read_conf_role_excel(conf_role)
    for index, row in df.iterrows():
        print(row['FirstName'], row['LastName'])
        roleID = get_conf_roleID(confRoles, row['Role'], confYear)
        print("roleID ", roleID)
        conferenceNo = confYear - 1974
        print(row['FirstName'], row['LastName'], row['Role'], roleID, conferenceNo)
        dbConnection.insert_conference_res_entry(row['FirstName'], row['LastName'], row['OrcID'],
                                              row['Affiliation'], row['Location'], row['Country'], conferenceNo,
                                              roleID)


def write_conf_role_to_db(df):
    db = DB("sqlite")
    for index, row in df.iterrows():
        if row['RoleID'] != 'x':
            db.insert_conf_role(row['Role'])


def get_conf_roleID(confRoles, role, year):
    print("Role: " + role)
    id = confRoles[confRoles[year] == role].RoleID.item()
    if id is None:
        return print("Error ID not found")
    else:
        return id


# basic cleaning
def init_run(confYear, mode):
    fileNumber = 2020 - confYear
    # basic separation of the string in name and affiliation
    df = dc.sort_conf_excel(conf_file, fileNumber, mode)
    # basic replacement of strings
    df = dc.preclean(df)
    # separates the affiliation string
    df = dc.sort_affiliation_string(df)
    # correct affiliations by substituting
    df = dc.correct_affiliations(df)
    # separates the affiliation string
    df = dc.sort_affiliation_string(df)
    # print(df.to_string())
    # unifies name from dict
    df = dc.correct_name(df)

    # add affiliations if missing
    df = dc.fill_affiliation_from_db(df)
    print(df.to_string())
    ex.write_csv(df, 'VLDB{}'.format(confYear))


# manual sorting
def manual_compare(confYear):
    # read as dataframe
    df = ex.read_csv('VLDB{}'.format(confYear))
    print(df.to_string())
    # compare affiliation with db
    dc.compare_affiliation_with_db(df)


# automated adding from db
def db_fill(confYear):
    # read as dataframe
    df = ex.read_csv('VLDB{}'.format(confYear))
    # add stuff from db
    df = dc.fill_affiliation_from_db(df)
    df = dc.fill_country_location_from_db(df)
    print(df.to_string())
    # write csv
    ex.write_csv(df, 'VLDB{}'.format(confYear))


def print_file(confYear):
    df = ex.read_csv('VLDB{}'.format(confYear))
    print(df.to_string())


# add orcid
def fill_orcid(confYear):
    # add orcid to dataframe
    df = dc.add_orcid(confYear)


def check_for_None(confYear):
    df = ex.read_csv('VLDB{}'.format(confYear))
    df = df.loc[df['Country'].isna()]
    print(df.to_string())

# write multiple csv to db
def write_to_db(start, end):
    db = DB("sqlite")
    db.reset()
    for i in range(start, end - 1, -1):
        print("JOURNAL:", i)
        write_journal_to_db('VLDB{}'.format(i), db, i)


if __name__ == '__main__':
    db = DB("sqlite")
    #db.reset_conf()
    confYear = 2012

    # print(df.to_string())

    # init_run(confYear, "comma")
    # manual_compare(confYear)
    # db_fill(confYear)
    # fill_orcid(confYear)
    # print_file(confYear)
    # check_for_None(confYear)
    write_conf_to_db('VLDB{}'.format(confYear), db, confYear)


    # sql queries
    # print(sql.get_journal(journalVol))

    # country statistics
    # df2 = get_country_stat()
    # ex.write_csv(df2, 'country_stat')
    # print(df2)
