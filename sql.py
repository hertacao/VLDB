import pandas as pd
from db_connect import *

countrySQL = "SELECT COUNT(*) AS Value, Country FROM \
             (SELECT DISTINCT(PersonID), AffiliationID FROM journal_responsibility \
             ORDER BY JournalVol DESC) journal_res \
             LEFT JOIN \
             affiliation \
             ON journal_res.AffiliationID = affiliation.AffiliationID \
             LEFT JOIN \
             country \
             ON affiliation.CountryID = country.CountryID \
             GROUP BY Country"

journalSQL = "SELECT FirstName, LastName, Role, Affiliation, Country FROM \
             (SELECT * FROM journal_responsibility WHERE JournalVol = {}) journal_res \
             INNER JOIN \
             person \
             ON journal_res.PersonID = person.PersonID \
             LEFT JOIN \
             affiliation \
             ON journal_res.AffiliationID = affiliation.AffiliationID \
             LEFT JOIN \
             country \
             ON affiliation.CountryID = country.CountryID \
             LEFT JOIN \
             journal_role \
             ON journal_res.RoleID = journal_role.RoleID"

affiliationsPerPersonSQL = "SELECT FirstVol, affiliation.AffiliationID, Affiliation FROM \
                ( SELECT AffiliationID, MIN(JournalVol) AS FirstVol FROM journal_responsibility \
                INNER JOIN \
                person \
                ON journal_responsibility.PersonID = person.PersonID \
                WHERE FirstName = '{}' AND LastName = '{}' \
                GROUP BY AffiliationID) affiliations \
                LEFT JOIN \
                affiliation \
                ON affiliations.AffiliationID = affiliation.AffiliationID"


personPerAffiliationSQL = "SElECT FirstName, LastName, JournalVol FROM \
                            (SELECT AffiliationID FROM affiliation WHERE Affiliation = '{}') aff \
                            LEFT JOIN \
                            journal_responsibility \
                            ON journal_responsibility.AffiliationID = aff.AffiliationID \
                            LEFT JOIN \
                            person \
                            ON journal_responsibility.PersonID = person.PersonID"


def get_country_stat():
    return pd.read_sql(countrySQL, con=sqlite)


def get_journal(journalVol):
    return pd.read_sql(journalSQL.format(journalVol), con=sqlite)


def get_affiliation(firstname, lastname):
    return pd.read_sql(affiliationsPerPersonSQL.format(firstname, lastname), con=sqlite)