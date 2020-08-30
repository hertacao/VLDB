import requests
import re
import pandas as pd


def search_orcid(name):
    url_para = name.replace(' ', '%20')
    searchurl = "https://dblp.uni-trier.de/search/author?q=" + url_para
    r = requests.get(searchurl)
    html = r.text
    m = re.search(r"https://orcid.org/[0-9-]*", html)
    if m:
        return m.group()
    else:
        return None


def read_csv(filestring):
    df = pd.read_csv(filestring)
    return df


def read_excel(filestring, sheet):
    df = pd.read_excel(filestring, sheet_name=sheet, usecols='B:E', skiprows=4)
    return df


def get_lastname(name):
    name_list = name.split()
    lastname = name_list.pop()
    return lastname


def get_firstname(name):
    name_list = name.split()
    name_list.pop()
    surname = " ".join(name_list)
    return surname


def write_csv(df, filename):
    f = open(r'csv\\' + filename + ".csv", "w")
    f.write(df.to_csv(index=False, encoding='utf-8'))
    f.close()

def get_name(string):
    m = re.search('\([\w ]*\)', string)

    if m:
        name = string.replace(m.group(), '')
    else:
        name = string
    ex = re.compile('(^\s*)|(\s*$)')
    name = ex.sub('', name)
    return name

def get_affiliation(string):
    m = re.search('\([\w ]*\)', string)

    if m:
        affiliation = m.group().replace('(', '').replace(')', '')
        return affiliation
    else:
        return None

