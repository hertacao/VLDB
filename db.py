import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="vldb"
)

mycursor = mydb.cursor()

roleDict = {"Editor in Chief": 1, "Managing Editor": 2, "Member Advisory Board": 3,
            "Publication Editor": 4, "Associate Editor": 5, "Member Review Board": 6}

countrySQL = "SELECT COUNT(*) AS Value, Country FROM \
             (SELECT DISTINCT(personID), affiliationID FROM journal_responsibility) journal \
             LEFT JOIN \
             affiliation \
             ON journal.affiliationID = affiliation.affiliationID \
             GROUP BY Country"

journalSQL = "SELECT FirstName, LastName, Role, Affiliation, Country FROM \
             (SELECT * FROM journal_responsibility WHERE journalVol = %s) journal_res \
             INNER JOIN \
             person \
             ON journal_res.personID = person.personID \
             LEFT JOIN \
             affiliation \
             ON journal_res.affiliationID = affiliation.affiliationID \
             LEFT JOIN \
             role \
             ON journal_res.roleID = role.roleID"

def alter(sql):
    result = mycursor.execute(sql, multi=True)
    result.send(None)


def reset():
    try:
        alter("DELETE FROM journal_responsibility")
        alter("DELETE FROM person")
        alter("DELETE FROM affiliation")
        alter("ALTER TABLE journal_responsibility AUTO_INCREMENT = 1")
        alter("ALTER TABLE person AUTO_INCREMENT = 1")
        alter("ALTER TABLE affiliation AUTO_INCREMENT = 1")
        mydb.commit()
        print("database reseted")
    except Exception as e:
        mydb.rollback()
        raise e


def check(sql, val):
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    # gets the number of rows affected by the command executed
    row_count = mycursor.rowcount
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


def check_person(firstName, lastName):
    sql = "SELECT PersonID FROM person WHERE FirstName = %s AND LastName = %s"
    val = (firstName, lastName)
    return check(sql, val)


def check_affiliation(name):
    sql = "SELECT AffiliationID FROM affiliation WHERE Name = %s"
    val = (name,)
    return check(sql, val)


def check_journal_responsibility(journalVol, personID, roleID):
    sql = "SELECT * FROM journal_responsibility WHERE journalVol = %s AND personID = %s AND roleID = %s"
    val = (journalVol, personID, roleID)
    return check(sql, val)


def insert(sql, val):
    mycursor.execute(sql, val)
    mydb.commit()
    print(val, " record inserted, ID:", mycursor.lastrowid)
    return mycursor.lastrowid


def insert_affiliation(affiliation, country, forced=False):
    if not forced:
        affiliationID = check_affiliation(affiliation)
    else:
        affiliationID = False
    if not affiliationID:
        sql = "INSERT INTO affiliation (Affiliation, Country) VALUES (%s, %s)"
        val = (affiliation, country)
        return insert(sql, val)
    else:
        return affiliationID


def insert_person(firstName, lastName, orcID, forced=False):
    if not forced:
        personID = check_person(firstName, lastName)
    else:
        personID = False
    if not personID:
        sql = "INSERT INTO person (FirstName, LastName, OrcID) VALUES (%s, %s, %s)"
        val = (firstName, lastName, orcID)
        return insert(sql, val)
    else:
        return personID


def insert_journal_responsibility(journalVol, personID, roleID, affiliationID, forced=False):
    if not forced:
        journal_responsibility = check_journal_responsibility(journalVol, personID, roleID)
    else:
        journal_responsibility = False
    if not journal_responsibility:
        sql = "INSERT INTO journal_responsibility (journalVol, personID, roleID, affiliationID) VALUES (%s, %s, %s, %s)"
        val = (journalVol, personID, roleID, affiliationID)
        return insert(sql, val)


def insert_journal_entry(firstName, lastName, orcID, affiliation, country, journalVol, role):
    personID = insert_person(firstName, lastName, orcID)
    affiliationID = insert_affiliation(affiliation, country)
    roleID = roleDict.get(role)
    insert_journal_responsibility(journalVol, personID, roleID, affiliationID)


def get_journal(journalVol):
    mycursor.execute(journalSQL, (journalVol,))
    result = mycursor.fetchall()
    return result


def get_by_country():
    mycursor.execute(countrySQL)
    result = mycursor.fetchall()
    return result
