import requests
import re
import pandas as pd
import numpy as np
import jellyfish

name_separator = ['de', 'De', 'van', 'Van', 'von', 'Von']

def search_orcid(firstname, lastname):
    if firstname is None or lastname is None:
        return None
    print("search for", firstname, lastname)
    url_para = firstname + '%20' + lastname
    searchurl = "https://dblp.uni-trier.de/search/author?q=" + url_para
    r = requests.get(searchurl)
    html = r.text
    m = re.search(r"https://orcid.org/[0-9X-]+", html)
    if m:
        print(m.group())
        return m.group()
    else:
        print("no orcID")
        return None


def read_csv(csv):
    df = pd.read_csv(r'csv\\' + csv + ".csv")
    # df = df.astype(str)
    df = df.replace({np.nan: None})
    return df

def read_conf_role_excel(filestring):
    df = pd.read_excel(filestring, sheet_name="Conference Role")
    df = df.replace({np.nan: None})
    return df


def read_excel(filestring, sheet):
    df = pd.read_excel(filestring, sheet_name=sheet, usecols='B:E', skiprows=4)
    df = df.replace({np.nan: None})
    return df


def read_conf_excel(filestring, sheet):
    df = pd.read_excel(filestring, sheet_name=sheet, usecols='B,F', skiprows=1)
    df = df.replace({np.nan: None})
    return df


def get_lastname(name_string):
    if name_string is None:
        return None
    for sep in name_separator:
        m = re.search(' ' + sep + ' ', name_string)
        if m:
            name_list = name_string.split(sep)
            lastname = sep.lower() + name_list.pop()
            return lastname

    name_list = name_string.split()
    lastname = name_list.pop()
    return lastname


def get_firstname(name_string):
    if name_string is None:
        return None
    for sep in name_separator:
        m = re.search(' ' + sep + ' ', name_string)
        if m:
            name_list = name_string.split(' ' + sep + ' ')
            return name_list[0]

    name_list = name_string.split()
    name_list.pop()
    surname = " ".join(name_list)
    return surname


def get_comma_affiliation(string):
    if len(string.split(",")) > 1:
        return drop_spaces(string.split(",")[1])
    else:
        return None


def get_comma_country(string):
    if len(string.split(",")) > 2:
        return drop_spaces(string.split(",")[2])
    else:
        return None

# drop leading or trailing spaces for a given string
def drop_spaces(string):
    if string is None:
        return None
    string = re.sub('(^\s*)|(\s*$)', '', string)
    return string


def write_csv(df, filename):
    f = open(r'csv\\' + filename + ".CSV", "w")
    f.write(df.to_csv(index=False, line_terminator='\n'))
    f.close()


# extract name from the string
def get_name_from_string(string):
    if string is None:
        return None
    m = re.search('\(.*\)', string)

    if m:
        name = string.replace(m.group(), '')
    else:
        name = string
    name = drop_spaces(name)
    return name


# extract affiliation from the string with brackets
def get_affiliation_from_string(string):
    if string is None:
        return None
    m = re.search('\(.*\)', string)

    if m:
        affiliation = m.group().replace('(', '').replace(')', '')
        return str(affiliation)
    else:
        return None


# extract affiliation from the affiliation with country
def get_affiliation_from_aff_extended(affiliation_string):
    global string_list
    if affiliation_string is None:
        return None
    if "," in affiliation_string:
        string_list = affiliation_string.split(",")
    elif "-" in affiliation_string:
        string_list = affiliation_string.split("-")
    else:
        string_list = []
    if len(string_list) > 1:
        string_list.pop()
        aff = " ".join(string_list)
        aff = drop_spaces(aff)
        return aff
    else:
        return affiliation_string


# get info (Country or Location) from affiliation string
def get_info_from_aff_extended(affiliation_string):
    global string_list
    if affiliation_string is None:
        return None
    if "," in affiliation_string:
        string_list = affiliation_string.split(",")
    elif "-" in affiliation_string:
        string_list = affiliation_string.split("-")
    elif " at " in affiliation_string:
        string_list = affiliation_string.split("at")
    else:
        string_list = []
    if len(string_list) > 1:
        info = string_list.pop()
        info = drop_spaces(info)
        return info
    else:
        return None


def replace_tu(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('TU\s', 'Technical University of ', affiliation)
    return affiliation


def replace_univ(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('(\s|^)U(niv)?\.?(\s|$)', ' University ', affiliation)
    return affiliation


def replace_uc(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('UC\s', 'University of California, ', affiliation)
    return affiliation


def replace_tech(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('\sTech(\s|$)', ' Institute of Technology', affiliation)
    return affiliation


def replace_iit(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('IIT\s', 'Indian Institute of Technology, ', affiliation)
    return affiliation

def replace_umass(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('UMass\s', 'University of Massachusetts, ', affiliation)
    return affiliation

def drop_the(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('^The\s', '', affiliation)
    return affiliation


def replace_usa(affiliation):
    if affiliation is None:
        return None
    affiliation = re.sub('USA', 'United States', affiliation)
    return affiliation

def remove_mail(string):
    if string is None:
        return None
    m = re.search('<.*>', string)

    if m:
        name = remove_comma(string.replace(m.group(), ''))
    else:
        name = string
    name = drop_spaces(name)
    return name

def remove_comma(string):
    if string is None:
        return None
    m = re.search(',', string)

    if m:
        name = string.replace(m.group(), '')
    else:
        name = string
    name = drop_spaces(name)
    return name

abbreviations = {
    "AIST": "National Institute of Advanced Industrial Science and Technology",
    "Alibaba": "Alibaba Group",
    "ANU": "Australian National University",
    "ASU": "Arizona State University",
    "AUB": "American University of Beirut",
    "BUPT": "Beijing University of Posts and Telecommunications",
    "CMU": "Carnegie Mellon University",
    "CNRS": "French National Centre for Scientific Research",
    "CUHK": "Chinese University of Hong Kong",
    "CUNY": "City University of New York",
    "CWI": "Centrum Wiskunde & Informatica",
    "DFKI": "German Research Center for Artificial Intelligence",
    "EPFL": "École polytechnique fédérale de Lausanne",
    "ETH": "ETH Zurich",
    "HKUST": "Hong Kong University of Science and Technology",
    "HKBU": "Hong Kong Baptist University",
    "HMC": "Harvey Mudd College",
    "HPI": "Hasso Plattner Institute",
    "ISI": "University of Southern California, Information Sciences Institute",
    "ISTAT": "Italian National Institute of Statistics",
    "ITU": "International Telecommunication Union",
    "JHU": "Johns Hopkins University",
    "KAUST": "King Abdullah University of Science and Technology",
    "KAIST": "Korea Advanced Institute of Science and Technology",
    "LNCC": "National Laboratory of Scientific Computation",
    "METU": "Middle East Technical University",
    "MIT": "Massachusetts Institute of Technology",
    "Microsoft": "Microsoft Research",
    "MPI": "Max Planck Institute",
    "NTU": "Nanyang Technological University",
    "NUS": "National University of Singapore",
    "NYU": "New York University",
    "NJIT": "New Jersey Institute of Technology",
    "NMSU": "New Mexico State University",
    "OSU": "Ohio State University",
    "Postech": "Pohang University of Science and Technology",
    "POSTECH": "Pohang University of Science and Technology",
    "PSU": "Pennsylvania State University",
    "Politecnico di Milano": "Polytechnic University of Milan",
    "QCRI": "Qatar Computing Research Institute",
    "RMIT": "RMIT University",
    "Sapienza University di Rome": "Sapienza University of Rome",
    "SFU": "Simon Fraser University",
    "SNU": "Seoul National University",
    "SUNY": "State University of New York",
    "SUTD" : "Singapore University of Technology and Design",
    "Technion": "Technion – Israel Institute of Technology",
    "TUM" : "Technical University of Munich",
    "UBC": "University of British Columbia",
    "UC": "University of California",
    "UCI": "University of California, Irvine",
    "UCLA": "University of California, Los Angeles",
    "UCR": "University of California, Riverside",
    "UCSB": "University of California, Santa Barbara",
    "UCSD": "University of California, San Diego",
    "UESTC": "University of Electronic Science and Technology of China",
    "UIC": "University of Illinois",
    "UIUC": "University of Illinois, Urbana–Champaign",
    "UNSW": "University of New South Wales",
    "Universidade Federal do Amazonas": "Federal University of Amazonas",
    "Universite Paris Sud": "Paris-Sud University",
    "USC": "University of Southern California",
    "USTC": "University of Science and Technology of China",
    "UW": "University of Wisconsin",
    "WPI": "Worcester Polytechnic Institute"
}


def replace_abbreviations(affiliation):
    full_name = abbreviations.get(affiliation)
    if full_name:
        return full_name
    else:
        return affiliation


unified_names = {
    "Bhowmick": "Sourav S.",
    "Bernstein": "Philip A.",
    "Bizer": "Christian",
    "Böhlen": "Michael H.",
    "Bruno": "Nicolas",
    "Cafarella": "Michael J.",
    "Candan": "K. Selçuk",
    "Carey": "Michael J.",
    "Cha": "Sang Kyun",
    "Chen": "Arbee L. P.",
    "Cheng": "Reynold",
    "Cudré-Mauroux": "Philippe",
    "Deshpande": "Amol",
    "Dong": "Xin Luna",
    "Eltabakh": "Mohamed Y.",
    "Gedik": "Bugra",
    "Han": "Wook-Shin",
    "Hwang": "Seung-won",
    "Ilyas": "Ihab F.",
    "Ives": "Zachary G.",
    "Jagadish": "H. V.",
    "Jermaine": "Chris",
    "Kennedy": "Oliver",
    "Kifer": "Daniel",
    "Kossmann": "Donald",
    "Lakshmanan": "Laks V.S.",
    "Madden": "Samuel",
    "Mansour": "Essam",
    "Marian": "Amélie",
    "Miller": "Renée J.",
    "Mokbel": "Mohamed F.",
    "Moro": "Mirella Moura",
    "Nascimento": "Mario A.",
    "Polyzotis": "Neoklis",
    "Patel": "Jignesh M.",
    "Pavlo": "Andrew",
    "Porto": "Fábio",
    "Ports": "Dan R. K.",
    "Quamar": "Abdul",
    "Ross": "Kenneth A.",
    "Rusu": "Florin ",
    "Ruiz": "Jorge Arnulfo Quiane",
    "Salles": "Marcos Antonio Vaz",
    "Salem": "Kenneth",
    "Sapino": "Maria Luisa",
    "Sattler": "Kai-Uwe",
    "Sariyüce": "A. Erdem",
    "Tung": "Anthony K. H.",
    "Özsu": "M. Tamer",
    "Wong": "Raymond Chi-Wing"
}


def replace_name_by_dict(firstname, lastname):
    if lastname in unified_names:
        return replace_name(firstname, unified_names[lastname])
    else:
        return firstname


def replace_name(firstname, comparision):
    print("firstname: {}    compare: {} ".format(firstname, comparision))
    levenshtein = jellyfish.levenshtein_distance(firstname, comparision)
    jaro_winkler = jellyfish.jaro_winkler_similarity(firstname, comparision)
    print("levensthein: {}    jaro-winkler: {}".format(levenshtein, jaro_winkler))

    if jaro_winkler >= 0.8:
        return comparision
    else:
        return firstname
