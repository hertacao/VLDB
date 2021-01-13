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

    """
    def alter(self, sql):
        result = self.cursor.execute(sql, multi=True)
        result.send(None)

    def reset_mysql(self):
        try:
            self.alter("DELETE FROM journal_responsibility")
            self.alter("DELETE FROM person")
            self.alter("DELETE FROM affiliation")
            self.alter("ALTER TABLE journal_responsibility AUTO_INCREMENT = 1")
            self.alter("ALTER TABLE person AUTO_INCREMENT = 1")
            self.alter("ALTER TABLE affiliation AUTO_INCREMENT = 1")
            self.conn.commit()
            print("database resetted")
        except Exception as e:
            self.conn.rollback()
            raise e
    """

    def reset(self):
        self.cursor.execute("DELETE FROM journal_responsibility")
        self.cursor.execute("DELETE FROM person")
        self.cursor.execute("DELETE FROM affiliation")
        self.cursor.execute("DELETE FROM country WHERE Region IS NULL")
        self.cursor.execute("DELETE FROM sqlite_sequence")
        self.conn.commit()

    def check(self, sql, val):
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result is None:
            return None
        else:
            if len(result) == 1:
                # print(val, "record exists, ID:", result[0])
                return result[0]
            else:
                # print(val, "record exists", result)
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

    def check_journal_responsibility(self, journalVol, personID, roleID):
        sql = "SELECT * FROM journal_responsibility WHERE JournalVol = ? AND PersonID = ? AND RoleID = ?"
        val = (journalVol, personID, roleID)
        return self.check(sql, val)

    def get_country_of_affiliation(self, name):
        sql = "SELECT Country FROM \
                (SELECT CountryID FROM affiliation WHERE Affiliation = ?) aff \
                LEFT JOIN \
                country \
                ON country.CountryID = aff.CountryID"
        val = (name,)
        return self.check(sql, val)

    def get_affiliation_from_name(self, firstname, lastname):
        sql = "SELECT Affiliation, Location FROM \
        (SELECT PersonID FROM person WHERE FirstName = ? AND LastName = ?) pers \
        LEFT JOIN \
        journal_responsibility \
        ON journal_responsibility.PersonID = pers.personID \
        LEFT JOIN \
        affiliation \
        ON journal_responsibility.AffiliationID = affiliation.AffiliationID \
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

    def insert_journal_responsibility(self, journalVol, personID, roleID, affiliationID, forced=False):
        if not forced:
            journal_responsibility = self.check_journal_responsibility(journalVol, personID, roleID)
        else:
            journal_responsibility = False
        if not journal_responsibility:
            sql = "INSERT INTO journal_responsibility (JournalVol, PersonID, RoleID, AffiliationID) VALUES (?, ?, ?, ?)"
            val = (journalVol, personID, roleID, affiliationID)
            return self.insert(sql, val)

    def insert_journal_res_entry(self, firstName, lastName, orcID, affiliation, location, country, journalVol, role):
        personID = self.insert_person(firstName, lastName, orcID)
        affiliationID = self.insert_affiliation_entry(affiliation, location, country)
        roleID = roleDict.get(role)
        self.insert_journal_responsibility(journalVol, personID, roleID, affiliationID)
        print(personID, roleID, affiliationID)

