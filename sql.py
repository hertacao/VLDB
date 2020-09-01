roleDict = {"Founding Editor in Chief": 1, "Editor in Chief": 2, "Managing Editor": 3,
            "Member Advisory Board": 4, "Publication Editor": 5, "Associate Editor": 6,
            "Member Review Board": 7, "Information Director": 8}

roleDictOld = {"Editor in Chief": 9, "General Program Chair": 10, "Program Chair": 11,
               "Proceedings Chair": 12, "Information Director": 13, "Steering Committee": 14}

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
             (SELECT * FROM journal_responsibility WHERE JournalVol = %s) journal_res \
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
             role \
             ON journal_res.RoleID = role.RoleID"


class DB:
    conn = 0
    cursor = 0
    OLD_JOURNAL_VOLUMES = 4

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def close(self):
        self.conn.close()

    def alter(self, sql):
        result = self.cursor.execute(sql, multi=True)
        result.send(None)

    def reset(self):
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

    def check(self, sql, val):
        self.cursor.execute(sql, val)
        results = self.cursor.fetchall()
        # gets the number of rows affected by the command executed
        row_count = self.cursor.rowcount
        if row_count == 0:
            return False
        if row_count == 1:
            result = results.pop()
            if len(result) == 1:
                print(val, "record exists, ID:", result[0])
                return result[0]
            else:
                print(val, "record exists", result)
                return result
        else:
            raise Exception("multiple entries found", results)

    def check_country(self, country):
        sql = "SELECT CountryID FROM country WHERE Country = %s"
        val = (country, )
        return self.check(sql, val)

    def check_person(self, firstName, lastName):
        sql = "SELECT PersonID FROM person WHERE FirstName = %s AND LastName = %s"
        val = (firstName, lastName)
        return self.check(sql, val)

    def check_affiliation(self, name):
        sql = "SELECT AffiliationID FROM affiliation WHERE Affiliation = %s"
        val = (name,)
        return self.check(sql, val)

    def check_journal_responsibility(self, journalVol, personID, roleID):
        sql = "SELECT * FROM journal_responsibility WHERE JournalVol = %s AND PersonID = %s AND RoleID = %s"
        val = (journalVol, personID, roleID)
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
            sql = "INSERT INTO country (Country, Region) VALUES (%s, %s)"
            val = (country, region)
            return self.insert(sql, val)
        else:
            return countryID

    def insert_affiliation(self, affiliation, countryID, forced=False):
        if not forced:
            affiliationID = self.check_affiliation(affiliation)
        else:
            affiliationID = False
        if not affiliationID:
            sql = "INSERT INTO affiliation (Affiliation, CountryID) VALUES (%s, %s)"
            val = (affiliation, countryID)
            return self.insert(sql, val)
        else:
            return affiliationID

    def insert_affiliation_entry(self, affiliation, country):
        countryID = self.insert_country(country, None)
        affiliationID = self.insert_affiliation(affiliation, countryID)
        return affiliationID

    def insert_person(self, firstName, lastName, orcID, forced=False):
        if not forced:
            personID = self.check_person(firstName, lastName)
        else:
            personID = False
        if not personID:
            sql = "INSERT INTO person (FirstName, LastName, OrcID) VALUES (%s, %s, %s)"
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
            sql = "INSERT INTO journal_responsibility (JournalVol, PersonID, RoleID, AffiliationID) VALUES (%s, %s, %s, %s)"
            val = (journalVol, personID, roleID, affiliationID)
            return self.insert(sql, val)

    def insert_journal_res_entry(self, firstName, lastName, orcID, affiliation, country, journalVol, role):
        personID = self.insert_person(firstName, lastName, orcID)
        affiliationID = self.insert_affiliation_entry(affiliation, country)
        roleID = roleDict.get(role)
        self.insert_journal_responsibility(journalVol, personID, roleID, affiliationID)

    def get_journal(self, journalVol):
        self.cursor.execute(journalSQL, (journalVol,))
        result = self.cursor.fetchall()
        return result

    def get_by_country(self):
        self.cursor.execute(countrySQL)
        result = self.cursor.fetchall()
        return result
