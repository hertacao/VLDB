import requests
import re
import pandas as pd
import numpy as np
import jellyfish


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


def read_excel(filestring, sheet):
    df = pd.read_excel(filestring, sheet_name=sheet, usecols='B:E', skiprows=4)
    df = df.replace({np.nan: None})
    return df


def get_lastname(name_string):
    if name_string is None:
        return None
    name_list = name_string.split()
    lastname = name_list.pop()
    return lastname


def get_firstname(name_string):
    if name_string is None:
        return None
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
    elif "at" in affiliation_string:
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


abbreviations = {
    "Microsoft": "Microsoft Research",
    "Alibaba": "Alibaba Group",
    "QCRI": "Qatar Computing Research Institute",
    "CWI": "Centrum Wiskunde & Informatica",
    "NUS": "National University of Singapore",
    "NJIT": "New Jersey Institute of Technology",
    "HKUST": "Hong Kong University of Science and Technology",
    "NMSU": "New Mexico State University",
    "UBC": "University of British Columbia",
    "ASU": "Arizona State University",
    "KAUST": "King Abdullah University of Science and Technology",
    "BUPT": "Beijing University of Posts and Telecommunications",
    "UESTC": "University of Electronic Science and Technology of China",
    "UCSB": "University of California, Santa Barbara",
    "HKBU": "Hong Kong Baptist University",
    "DFKI": "German Research Center for Artificial Intelligence",
    "UNSW": "University of New South Wales",
    "RMIT": "RMIT University",
    "METU": "Middle East Technical University",
    "WPI": "Worcester Polytechnic Institute",
    "CMU": "Carnegie Mellon University",
    "LNCC": "National Laboratory of Scientific Computation",
    "MIT": "Massachusetts Institute of Technology",
    "CUNY": "City University of New York",
    "UW": "University of Wisconsin",
    "NYU": "New York University",
    "EPFL": "École polytechnique fédérale de Lausanne",
    "SFU": "Simon Fraser University",
    "AUB": "American University of Beirut",
    "UCS": "University of Southern California",
    "CNRS": "French National Centre for Scientific Research",
    "UCLA": "University of California, Los Angeles",
    "Postech": "Pohang University of Science and Technology",
    "POSTECH": "Pohang University of Science and Technology",
    "AIST": "National Institute of Advanced Industrial Science and Technology",
    "HPI": "Hasso Plattner Institute",
    "KAIST": "Korea Advanced Institute of Science and Technology",
    "JHU": "Johns Hopkins University",
    "ISI": "University of Southern California, Information Sciences Institute",
    "CUHK": "Chinese University of Hong Kong",
    "MPI": "Max Planck Institute",
    "PSU": "Pennsylvania State University",
    "ISTAT": "Italian National Institute of Statistics",
    "NTU": "Nanyang Technological University",
    "SNU": "Seoul National University",
    "SUNY": "State University of New York"
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
    "Mansour": "Essam",
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
