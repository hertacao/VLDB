import excel as ex
from sql import *
import db

db = db.DB("sqlite")


def sort_excel(filestring, sheet, mode):
    sorter = {
        "sep": sort_excel_sep_aff(filestring, sheet),
        "join": sort_excel_string(filestring, sheet),
        "comma": sort_excel_comma(filestring, sheet)
    }
    return sorter.get(mode, sort_excel_string(filestring, sheet))


# simple function to correct any mistakes in the data
# creates separate column for first and last name
# cleans affiliations when they are given in a separate column
def sort_excel_sep_aff(filestring, sheet):
    df = ex.read_excel(filestring, sheet)
    df.insert(1, 'FirstName', [ex.get_firstname(name) for name in df['Name']])
    df.insert(2, 'LastName', [ex.get_lastname(name) for name in df['Name']])
    print("names inserted")

    df['Affiliation'] = [ex.drop_spaces(string) for string in df['Affiliation']]
    df.insert(4, 'Location', None)
    df['Country'] = None
    df['OrcID'] = None
    return df


# simple function to correct any mistakes in the data
# creates separate column for first and last name
# extracts affiliations from a combined string of name and affiliation
def sort_excel_string(filestring, sheet):
    df = ex.read_excel(filestring, sheet)
    df.insert(1, 'FirstName', [ex.get_firstname(ex.get_name_from_string(string)) for string in df['Name']])
    df.insert(2, 'LastName', [ex.get_lastname(ex.get_name_from_string(string)) for string in df['Name']])
    print("names inserted")

    df['Affiliation'] = [ex.get_affiliation_from_string(string) for string in df['Name']]
    df.insert(4, 'Location', None)
    df['Country'] = None
    df['OrcID'] = None
    print("affiliation inserted")
    return df


def sort_excel_comma(filestring, sheet):
    df = ex.read_excel(filestring, sheet)
    df.insert(1, 'FirstName', [ex.get_firstname(string.split(",")[0]) for string in df['Name']])
    df.insert(2, 'LastName', [ex.get_lastname(string.split(",")[0]) for string in df['Name']])
    print("names inserted")

    df['Affiliation'] = [ex.get_comma_affiliation(string) for string in df['Name']]
    df.insert(4, 'Location', None)
    df['Country'] = [ex.get_comma_country(string) for string in df['Name']]
    df['OrcID'] = None
    print("affiliation inserted")
    return df


# sorts the affiliation string in affiliation, location and country
def sort_affiliation_string(df):
    df['Info'] = [ex.get_info_from_aff_extended(affiliation_string) for affiliation_string in df['Affiliation']]

    df['isCountry'] = [db.check_country(info) for info in df['Info']]
    df.loc[df['isCountry'] > 0, 'isCountry'] = True
    df.loc[df['Country'].isnull() & df['isCountry'], 'Country'] = df['Info']
    df.loc[df['Location'].isnull() & (df['isCountry'] is False), 'Location'] = df['Info']
    df = df.drop(columns=['Info', 'isCountry'])
    print("country/location inserted")

    df['Affiliation'] = [ex.get_affiliation_from_aff_extended(affiliation) for affiliation in df['Affiliation']]
    print("affiliation inserted")
    return df


def add_orcid(journalVol):
    df = ex.read_csv('VLDB{}'.format(journalVol))
    start = 0
    if 'OrcID' not in df.columns:
        print("insert column")
        df['OrcID'] = None
    for idx in reversed(df.index):
        if df.OrcID[idx] is not None:
            start = idx + 1
            break
        elif idx == 0:
            start = 0
    for index, row in df.iloc[start:].iterrows():
        row['OrcID'] = ex.search_orcid(row['FirstName'], row['LastName'])
        if index % 5 == 4:
            ex.write_csv(df, 'VLDB{}'.format(journalVol))
            print("write OrcID to csv")
    ex.write_csv(df, 'VLDB{}'.format(journalVol))
    return df


def preclean(df):
    corrected = [ex.replace_usa(affiliation) for affiliation in df['Affiliation']]
    df['Affiliation'] = corrected
    return df


def correct_affiliations(df):
    corrected = [ex.replace_abbreviations(affiliation) for affiliation in df['Affiliation']]
    corrected = [ex.replace_tu(affiliation) for affiliation in corrected]
    corrected = [ex.replace_univ(affiliation) for affiliation in corrected]
    corrected = [ex.replace_uc(affiliation) for affiliation in corrected]
    corrected = [ex.drop_the(affiliation) for affiliation in corrected]
    corrected = [ex.replace_tech(affiliation) for affiliation in corrected]
    corrected = [ex.replace_iit(affiliation) for affiliation in corrected]

    df['Affiliation'] = [ex.drop_spaces(affiliation) for affiliation in corrected]

    return df


# stats
csv_match = 0
matches = []
no_record = []
mismatch = []
multiple_aff = []
aff_not_found = []


# retrieves affiliation from the db for a given name
def add_affiliation_from_db(firstname, lastname, affiliation, location):
    if affiliation is None or affiliation == "None":
        db_affiliation = db.get_affiliation_from_name(firstname, lastname)
        if db_affiliation:
            return db_affiliation
        else:
            return None, None
    elif location is None or location == "None":
        db_affiliation = db.get_affiliation_from_name(firstname, lastname)
        if db_affiliation is not None:
            if affiliation == db_affiliation[0]:
                return db_affiliation
            else:
                return affiliation, location

        else:
            return affiliation, None
    else:
        return affiliation, location


# fills up dataframe with affiliation extracted from the database
def fill_affiliation_from_db(df):
    affiliations = [add_affiliation_from_db(firstname, lastname, affiliation, location) for firstname, lastname, affiliation, location in
                    zip(df['FirstName'], df['LastName'], df['Affiliation'], df['Location'])]
    df[['Affiliation', 'Location']] = pd.DataFrame(affiliations, index=df.index)
    print("affiliation added")
    return df


# adds country from the database for an affiliation
def add_country_from_db(affiliation, country):
    if country is None:
        db_country = db.get_country_of_affiliation(affiliation)
        if db_country:
            return db_country
        else:
            return None
    else:
        return country


# fills up countries for a dataframe
def fill_country_from_db(df):
    if 'Country' not in df:
        df['Country'] = None
    df['Country'] = [add_country_from_db(affiliation, country) for affiliation, country in
                     zip(df['Affiliation'], df['Country'])]
    print("country added")
    return df


# checks the affiliations of a dataframe with db
def compare_affiliation_with_db(df):
    global no_record, aff_not_found
    for index, row in df.iterrows():
        print()
        print(row['FirstName'], row['LastName'])
        if db.check_person(row['FirstName'], row['LastName']):
            compare_affiliation(row['FirstName'], row['LastName'], row["Affiliation"])
        else:
            no_record.append(row['FirstName'] + " " + row['LastName'])
            print("not contained")
            # looks for the affiliation itself
            if db.check_affiliation(row["Affiliation"], None):
                print("affiliation found")
            else:
                aff_not_found.append(
                    {"FirstName": row['FirstName'], "LastName": row['LastName'], "Affiliation": row["Affiliation"]})
                print("affiliation NOT found")
            print("csv:", row["Affiliation"])

    print()
    print("=============================================")
    print("no records of person:", len(no_record))
    print("affiliation matches:", len(matches))
    print("affiliation mismatch:", len(mismatch))
    print("multiple affiliations:", len(multiple_aff))
    print("---------------------------------------------")
    print("csv matches:", csv_match)
    print("affiliations not found:", len(aff_not_found))

    df_mismatch = pd.DataFrame(mismatch)
    df_not_found = pd.DataFrame(aff_not_found)
    print()
    print()
    print("Affiliation of csv and database unequal")
    print(df_mismatch.to_string())
    print()
    print("Affiliation not found in database")
    print(df_not_found.to_string())


# compares affiliation in csv with db for a single row
def compare_affiliation(firstname, lastname, csv_affiliation):
    # looks in the db for affiliation associated with this person
    affiliation_df = get_affiliation(firstname, lastname)
    global matches, mismatch, multiple_aff, csv_match, aff_not_found
    if len(affiliation_df.index) == 1:
        db_affiliation = affiliation_df["Affiliation"].item()
        if csv_affiliation == db_affiliation:
            matches.append(firstname + " " + lastname)
            print("affiliation matches")
        else:
            print("differences detected")
            print("db:", db_affiliation)
            print("csv:", csv_affiliation)
            # looks for the affiliation itself
            if db.check_affiliation(csv_affiliation, None):
                mismatch.append(
                    {"FirstName": firstname, "LastName": lastname, "db": db_affiliation, "csv": csv_affiliation, "found": True})
                csv_match += 1
                print("csv affiliation is in database")
            else:
                aff_not_found.append(
                    {"FirstName": firstname, "LastName": lastname, "Affiliation": csv_affiliation})
                mismatch.append(
                    {"FirstName": firstname, "LastName": lastname, "db": db_affiliation, "csv": csv_affiliation, "found": False})
                print("csv affiliation NOT found")
    else:
        multiple_aff.append(firstname + " " + lastname)
        print("multiple affiliations")
        print(affiliation_df)


def correct_name(df):
    df['FirstName'] = [ex.replace_name_by_dict(firstname, lastname) for firstname, lastname in zip(df['FirstName'], df['LastName'])]
    return df

