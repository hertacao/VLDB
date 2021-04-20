from db_connect import *

roleDict = {"Founding Editor in Chief": 1, "Editor in Chief": 2, "Managing Editor": 3,
            "Member Advisory Board": 4, "Publication Editor": 5, "Associate Editor": 6,
            "Member Review Board": 7, "Information Director": 8,
            "Technical Program Chair": 9, "General Program Chair": 10, "Track Chair": 11,
            "Proceedings Chair": 12, "Steering Committee": 13, "Proceedings Editor": 14}

class DB:
    conn = 0
    cursor = 0
    db = None
    OLD_JOURNAL_VOLUMES = 4

    @staticmethod
    def get_connection(dbname):
        connections = {
            'sqlite': sqlite,
        }
        return connections.get(dbname, "Invalid database")

    def __init__(self, dbname):
        self.conn = self.get_connection(dbname)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def reset(self):
        self.cursor.execute("DELETE FROM journal_responsibility")
        self.cursor.execute("DELETE FROM person")
        self.cursor.execute("DELETE FROM affiliation")
        self.cursor.execute("DELETE FROM person_affiliation")
        self.cursor.execute("DELETE FROM country WHERE Region IS NULL")
        self.cursor.execute("DELETE FROM sqlite_sequence")
        self.conn.commit()

    def reset_conf(self):
        self.cursor.execute("DELETE FROM conference_responsibility")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='conference_responsibility'")
        self.conn.commit()

    def check(self, sql, val):
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        if result is None or len(result) == 0:
            return None
        else:
            if len(result) == 1:
                if len(result[0]) == 1:
                    return result[0][0]
                else:
                    return result[0]
            elif len(result[0]) == 1:
                return [r[0] for r in result]
            else:
                return result

    def check_country(self, country):
        sql = "SELECT CountryID FROM country WHERE Country = ?"
        val = (country,)
        return self.check(sql, val)

    def check_person(self, firstName, lastName):
        sql = "SELECT PersonID FROM person WHERE FirstName = ? AND LastName = ?"
        val = (firstName, lastName)
        return self.check(sql, val)

    def check_affiliation(self, name, location):
        if location is None:
            sql = "SELECT AffiliationID FROM affiliation WHERE Affiliation = ?"
            val = (name,)
        else:
            sql = "SELECT AffiliationID FROM affiliation WHERE Affiliation = ? AND Location = ?"
            val = (name, location)
        return self.check(sql, val)

    def check_person_affiliation(self, personID, affiliationID):
        sql = "SELECT * FROM person_affiliation WHERE PersonID = ? AND AffiliationID = ?"
        val = (personID, affiliationID)
        return self.check(sql, val)

    def check_journal_responsibility(self, journalVol, personID, roleID):
        sql = "SELECT * FROM journal_responsibility WHERE JournalVol = ? AND PersonID = ? AND RoleID = ?"
        val = (journalVol, personID, roleID)
        return self.check(sql, val)

    def check_conference_responsibility(self, conferenceNo, personID, roleID):
        sql = "SELECT * FROM conference_responsibility WHERE ConferenceNo = ? AND PersonID = ? AND RoleID = ?"
        val = (conferenceNo, personID, roleID)
        return self.check(sql, val)

    def get_country_of_affiliation(self, affiliation, location):
        sql = "SELECT Country FROM \
                (SELECT CountryID FROM affiliation WHERE Affiliation = ? AND Location = ?) aff \
                LEFT JOIN \
                country \
                ON country.CountryID = aff.CountryID"
        val = (affiliation, location)
        return self.check(sql, val)

    def get_location_of_affiliation(self, name):
        sql = "SELECT Location FROM affiliation WHERE Affiliation = ?"
        val = (name,)
        return self.check(sql, val)

    def get_affiliation_from_name(self, firstname, lastname):
        sql = "SELECT Affiliation, Location FROM \
        (SELECT PersonID FROM person WHERE FirstName = ? AND LastName = ?) pers \
        LEFT JOIN \
        person_affiliation \
        ON person_affiliation.PersonID = pers.personID \
        LEFT JOIN \
        affiliation \
        ON person_affiliation.AffiliationID = affiliation.AffiliationID \
        GROUP BY affiliation.AffiliationID"
        val = (firstname, lastname)
        return self.check(sql, val)

    def insert(self, sql, val):
        self.cursor.execute(sql, val)
        self.conn.commit()
        print(val, " record inserted, ID:", self.cursor.lastrowid)
        return self.cursor.lastrowid

    def insert_country(self, country, region, forced=False):
        if not forced:
            countryID = self.check_country(country)
        else:
            countryID = False
        if not countryID:
            sql = "INSERT INTO country (Country, Region) VALUES (?, ?)"
            val = (country, region)
            return self.insert(sql, val)
        else:
            return countryID

    def insert_affiliation(self, affiliation, location, countryID, forced=False):
        if not forced:
            affiliationID = self.check_affiliation(affiliation, location)
        else:
            affiliationID = False
        if not affiliationID:
            sql = "INSERT INTO affiliation (Affiliation, Location, CountryID) VALUES (?, ?, ?)"
            val = (affiliation, location, countryID)
            return self.insert(sql, val)
        else:
            return affiliationID

    def insert_affiliation_entry(self, affiliation, location, country):
        countryID = self.insert_country(country, None)
        affiliationID = self.insert_affiliation(affiliation, location, countryID)
        return affiliationID

    def insert_person(self, firstName, lastName, orcID, forced=False):
        if not forced:
            personID = self.check_person(firstName, lastName)
        else:
            personID = False
        if not personID:
            sql = "INSERT INTO person (FirstName, LastName, OrcID) VALUES (?, ?, ?)"
            val = (firstName, lastName, orcID)
            return self.insert(sql, val)
        else:
            return personID

    def insert_person_affiliation(self, personID, affiliationID, forced=False):
        if not forced:
            person_affiliation = self.check_person_affiliation(personID, affiliationID)
        else:
            person_affiliation = False
        if not person_affiliation:
            sql = "INSERT INTO person_affiliation (PersonID, AffiliationID) VALUES (?, ?)"
            val = (personID, affiliationID)
            return self.insert(sql, val)

    def insert_journal_responsibility(self, journalVol, personID, roleID, affiliationID, forced=False):
        if not forced:
            journal_responsibility = self.check_journal_responsibility(journalVol, personID, roleID)
        else:
            journal_responsibility = False
        if not journal_responsibility:
            sql = "INSERT INTO journal_responsibility (JournalVol, PersonID, RoleID, AffiliationID) VALUES (?, ?, ?, ?)"
            val = (journalVol, personID, roleID, affiliationID)
            return self.insert(sql, val)

    def insert_conference_responsibility(self, conferenceNo, personID, roleID, affiliationID, forced=False):
        if not forced:
            journal_responsibility = self.check_conference_responsibility(conferenceNo, personID, roleID)
        else:
            journal_responsibility = False
        if not journal_responsibility:
            sql = "INSERT INTO conference_responsibility (ConferenceNo, PersonID, RoleID, AffiliationID) VALUES (?, ?, ?, ?)"
            val = (conferenceNo, personID, roleID, affiliationID)
            return self.insert(sql, val)

    def insert_journal_res_entry(self, firstName, lastName, orcID, affiliation, location, country, journalVol, role):
        personID = self.insert_person(firstName, lastName, orcID)
        affiliationID = self.insert_affiliation_entry(affiliation, location, country)
        self.insert_person_affiliation(personID, affiliationID)
        roleID = roleDict.get(role)
        self.insert_journal_responsibility(journalVol, personID, roleID, affiliationID)
        print(personID, roleID, affiliationID)

    def insert_conference_res_entry(self, firstName, lastName, orcID, affiliation, location, country, conferenceNo, roleID):
        personID = self.insert_person(firstName, lastName, orcID)
        affiliationID = self.insert_affiliation_entry(affiliation, location, country)
        self.insert_person_affiliation(personID, affiliationID)
        self.insert_conference_responsibility(conferenceNo, personID, roleID, affiliationID)
        print(personID, roleID, affiliationID)

    def insert_conf_role(self, confRole):
        sql = "INSERT INTO conference_role (Role) VALUES (?)"
        val = (confRole,)
        return self.insert(sql, val)

