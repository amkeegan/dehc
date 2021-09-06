import itertools
import random
import sys
from db import DEHC_Database

# ----------------------------------------------------------------------------

SURNAMES = ["Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", "Anderson", "Johnson", "White", "Thompson", "Lee", "Martin", "Thomas", "Walker", "Kelly", "Young", "Harris", "King", "Ryan", "Roberts", "Hall", "Evans", "Davis", "Wright", "Baker", "Campbell", "Edwards", "Clark", "Robinson", "McDonald", "Hill", "Scott", "Clarke", "Mitchell", "Stewart", "Moore", "Turner", "Miller", "Green", "Watson", "Bell", "Wood", "Cooper", "Murphy", "Jackson", "James", "Lewis", "Allen", "Bennett", "Robertson", "Collins", "Cook", "Murray", "Ward", "Phillips", "O'Brien", "Nguyen", "Davies", "Hughes", "Morris", "Adams", "Johnston", "Parker", "Ross", "Gray", "Graham", "Russell", "Morgan", "Reid", "Kennedy", "Marshall", "Singh", "Cox", "Harrison", "Simpson", "Richardson", "Richards", "Carter", "Rogers", "Walsh", "Thomson", "Bailey", "Matthews", "Cameron", "Webb", "Chapman", "Stevens", "Ellis", "McKenzie", "Grant", "Shaw", "Hunt", "Harvey", "Butler", "Mills", "Price", "Pearce", "Barnes", "Henderson", "Armstrong", "Fraser", "Fisher", "Knight", "Hamilton", "Mason", "Hunter", "Hayes", "Ferguson", "Dunn", "Wallace", "Ford", "Elliott", "Foster", "Gibson", "Gordon", "Howard", "Burns", "O'Connor", "Jenkins", "Woods", "Palmer", "Reynolds", "Holmes", "Black", "Griffiths", "McLean", "Day", "Andrews", "Lloyd", "Morrison", "West", "Duncan", "Wang", "Sullivan", "Rose", "Chen", "Powell", "Brooks", "Dawson", "MacDonald", "Dixon", "Wong", "Saunders", "Watts", "Francis", "Fletcher", "Tran", "Rowe", "Li", "Nelson", "Williamson", "Lawrence", "Porter", "Payne", "Byrne", "FitzGerald", "Crawford", "Barker", "Perry", "Hart", "Davidson", "Wilkinson", "Fox", "Cole", "Lane", "Kerr", "Lynch", "Webster", "Pearson", "McCarthy", "Doyle", "Stone", "Carroll", "Peters", "Stephens", "Freeman", "George", "Wells", "Alexander", "McMahon", "Tan", "Chan", "McGrath", "Spencer", "May", "Lowe", "Zhang", "Douglas", "Coleman", "O'Neill", "Barrett", "Boyd", "Burgess", "Sutton", "Burke", "Dean", "Atkinson", "Patterson", "Hogan", "Gill"]
M_NAMES = ["Oliver", "Kai", "Noah", "Jordan", "William", "Riley", "Leo", "Eli", "Lucas", "Louis", "Liam", "Aiden", "Jack", "Jasper", "Henry", "Austin", "Elijah", "Gabriel", "Thomas", "Beau", "James", "Michael", "Alexander", "Lincoln", "Charlie", "Flynn", "Levi", "Ali", "Theodore", "Carter", "Hudson", "Connor", "Jacob", "Charles", "Archie", "Sonny", "Ethan", "Spencer", "Harrison", "Jaxon", "Mason", "Zachary", "Hunter", "Ashton", "Isaac", "Jude", "Oscar", "Patrick", "Cooper", "Luke", "Lachlan", "Matthew", "Luca", "Owen", "George", "Isaiah", "Benjamin", "Nicholas", "Harry", "Luka", "Harvey", "Leonardo", "Samuel", "Christian", "Hugo", "Angus", "Max", "Marcus", "Archer", "Bodhi", "Sebastian", "Theo", "Arlo", "Leon", "Logan", "Asher", "Muhammad", "Jake", "Finn", "Axel", "Xavier", "Caleb", "Ryan", "Ryder", "Edward", "Dylan", "Arthur", "Dominic", "Jayden", "Ari", "Jackson", "Elias", "Joshua", "Felix", "Daniel", "Vincent", "Joseph", "Lennox", "Adam", "Anthony"]
F_NAMES = ["Amelia", "Freya", "Olivia", "Maya", "Charlotte", "Bonnie", "Mia", "Stella", "Isla", "Luna", "Ava", "Ayla", "Chloe", "Billie", "Grace", "Elizabeth", "Sophia", "Mackenzie", "Zoe", "Lola", "Harper", "Eloise", "Ivy", "Harriet", "Isabella", "Savannah", "Ella", "Aaliyah", "Sophie", "Rose", "Sienna", "Piper", "Matilda", "Daisy", "Willow", "Lara", "Lily", "Millie", "Evelyn", "Hallie", "Mila", "Elena", "Ruby", "Ariana", "Evie", "Sarah", "Layla", "Sadie", "Audrey", "Anna", "Emily", "Remi", "Lucy", "Phoebe", "Aria", "Olive", "Hannah", "Imogen", "Hazel", "Eliana", "Georgia", "Harlow", "Zara", "Annabelle", "Sofia", "Molly", "Scarlett", "Bella", "Ellie", "Addison", "Emma", "Summer", "Frankie", "Clara", "Abigail", "Claire", "Isabelle", "Eliza", "Florence", "Maddison", "Eva", "Gabriella", "Violet", "Zoey", "Emilia", "Delilah", "Elsie", "Isabel", "Eleanor", "Charlie", "Aurora", "Eden", "Penelope", "Adeline", "Jasmine", "Maeve", "Poppy", "Chelsea", "Alice", "Maryam"]
SERIAL = itertools.count(start=1, step=1)
F_SERIAL = itertools.count(start=1, step=1)
NATIONALITIES = ["AFG", "ALA", "ALB", "DZA", "ASM", "AND", "AGO", "AIA", "ATA", "ATG", "ARG", "ARM", "ABW", "AUS", "AUT", "AZE", "BHS", "BHR", "BGD", "BRB", "BLR", "BEL", "BLZ", "BEN", "BMU", "BTN", "BOL", "BES", "BIH", "BWA", "BVT", "BRA", "IOT", "BRN", "BGR", "BFA", "BDI", "CPV", "KHM", "CMR", "CAN", "CYM", "CAF", "TCD", "CHL", "CHN", "CXR", "CCK", "COL", "COM", "COD", "COG", "COK", "CRI", "CIV", "HRV", "CUB", "CUW", "CYP", "CZE", "DNK", "DJI", "DMA", "DOM", "ECU", "EGY", "SLV", "GNQ", "ERI", "EST", "SWZ", "ETH", "FLK", "FRO", "FJI", "FIN", "FRA", "GUF", "PYF", "ATF", "GAB", "GMB", "GEO", "DEU", "GHA", "GIB", "GRC", "GRL", "GRD", "GLP", "GUM", "GTM", "GGY", "GIN", "GNB", "GUY", "HTI", "HMD", "VAT", "HND", "HKG", "HUN", "ISL", "IND", "IDN", "IRN", "IRQ", "IRL", "IMN", "ISR", "ITA", "JAM", "JPN", "JEY", "JOR", "KAZ", "KEN", "KIR", "PRK", "KOR", "KWT", "KGZ", "LAO", "LVA", "LBN", "LSO", "LBR", "LBY", "LIE", "LTU", "LUX", "MAC", "MKD", "MDG", "MWI", "MYS", "MDV", "MLI", "MLT", "MHL", "MTQ", "MRT", "MUS", "MYT", "MEX", "FSM", "MDA", "MCO", "MNG", "MNE", "MSR", "MAR", "MOZ", "MMR", "NAM", "NRU", "NPL", "NLD", "NCL", "NZL", "NIC", "NER", "NGA", "NIU", "NFK", "MNP", "NOR", "OMN", "PAK", "PLW", "PSE", "PAN", "PNG", "PRY", "PER", "PHL", "PCN", "POL", "PRT", "PRI", "QAT", "REU", "ROU", "RUS", "RWA", "BLM", "SHN", "KNA", "LCA", "MAF", "SPM", "VCT", "WSM", "SMR", "STP", "SAU", "SEN", "SRB", "SYC", "SLE", "SGP", "SXM", "SVK", "SVN", "SLB", "SOM", "ZAF", "SGS", "SSD", "ESP", "LKA", "SDN", "SUR", "SJM", "SWE", "CHE", "SYR", "TWN", "TJK", "TZA", "THA", "TLS", "TGO", "TKL", "TON", "TTO", "TUN", "TUR", "TKM", "TCA", "TUV", "UGA", "UKR", "ARE", "GBR", "UMI", "USA", "URY", "UZB", "VUT", "VEN", "VNM", "VGB", "VIR", "WLF", "ESH", "YEM", "ZMB", "ZWE"]
IDS = []

# ----------------------------------------------------------------------------

def evacuee_gen(predata={}):
    #["Serial", "Evacuee ID", "Family Name", "Given Names", "Sex", "Date of Birth", "Passport Number", "Expiry", "Nationality", "Home Address", "Destination Address", "Contact Number", "Email", "Next of Kin", "Weight (KG)", "Authority to Release Information", "Requires Medical Attention", "Baggage Searched", "Evacuee Searched", "Dangerous Goods", "Misc"]
    serial = str(next(SERIAL))
    n = hex(random.randint(0, 281474976710656))[2:]
    evacueeid = "0"*(12-len(n))+n
    familyname = random.choice(SURNAMES)
    sex, = random.choices(population=["M", "F", "X"], weights=[50, 49, 1], k=1)
    givennames = random.choice({"M":M_NAMES, "F":F_NAMES, "X":random.choice([M_NAMES, F_NAMES])}[sex])
    dob = f"{random.randint(1930, 2020)}/{random.randint(1, 12)}/{random.randint(1, 28)}"
    passport = "M"+"".join([random.choice("0123456789") for _ in range(0,8)])
    expiry = f"{random.randint(2022, 2031)}/{random.randint(1, 12)}/{random.randint(1, 28)}"
    nationality, = random.choices(population=["AUS", random.choice(NATIONALITIES)], weights=[4, 1], k=1)
    homeaddress = f"{random.randint(1, 99)} Street, {random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}ville, {nationality}"
    destination = homeaddress if random.random() > 0.2 else f"{random.randint(1, 99)} Street, {random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}ville, AUS"
    contact = "0"+"".join([random.choice("0123456789") for _ in range(0,9)])
    email = f"{givennames.lower()}.{familyname.lower()}@mail.com".strip("'")
    nok = f"{familyname if random.random() > 0.2 else random.choice(SURNAMES)}, {random.choice({'M':M_NAMES, 'F':F_NAMES, 'X':random.choice([M_NAMES, F_NAMES])}[sex])}"
    authority, = random.choices(population=["Y", "N"], weights=[3, 1])
    medical, = random.choices(population=["Y", "N"], weights=[1, 99])
    bagsearch, = random.choices(population=["Y", "N"], weights=[99, 1])
    evacsearch, = random.choices(population=["Y", "N"], weights=[99, 1])
    dgoods, = random.choices(population=["Y", "N"], weights=[1, 99])
    data = {"Serial": serial, "Evacuee ID": evacueeid, "Family Name": familyname, "Given Names": givennames, "Sex": sex, "Date of Birth": dob, "Passport Number": passport, "Expiry": expiry, "Nationality": nationality, "Home Address": homeaddress, "Destination Address": destination, "Contact Number": contact, "Email": email, "Next of Kin": nok, "Authority to Release Information": authority, "Requires Medical Attention": medical, "Baggage Searched": bagsearch, "Evacuee Searched": evacsearch, "Dangerous Goods": dgoods}
    for key, value in predata.items():
        data[key] = value
    return data

def evacuee_add():
    data = evacuee_gen()
    id = db.item_add(category="Evacuee", data=data)
    IDS.append(id)

def family_add():
    serial = str(next(F_SERIAL))
    familyname = random.choice(SURNAMES)
    con = db.item_add(category="Family", data={"Serial": serial, "Name": f"{familyname} Family"})
    IDS.append(con)

    m1 = evacuee_gen({"Family Name":familyname})
    m2 = evacuee_gen({"Family Name":familyname, "Next of Kin": f"{m1['Family Name']}, {m1['Given Names']}", "Nationality": f"{m1['Nationality']}", "Home Address": f"{m1['Home Address']}", "Destination Address": f"{m1['Destination Address']}"})
    m1['Next of Kin'] = f"{m2['Family Name']}, {m2['Given Names']}"
    p1 = db.item_add(category="Evacuee", data=m1)
    p2 = db.item_add(category="Evacuee", data=m2)
    db.container_add(container=con, item=p1)
    db.container_add(container=con, item=p2)

    for _ in range(0, random.randint(0,3)):
        me = evacuee_gen({"Family Name":familyname, "Next of Kin": f"{m1['Family Name']}, {m1['Given Names']}", "Nationality": f"{m1['Nationality']}", "Home Address": f"{m1['Home Address']}", "Destination Address": f"{m1['Destination Address']}"})
        pe = db.item_add(category="Evacuee", data=me)
        db.container_add(container=con, item=pe)

# ----------------------------------------------------------------------------

db = DEHC_Database(create=False)

db.db_delete()
db.db_create()

s1 = db.item_add(category="Station", data={"Name":"Processing", "Index":"1", "Misc":"Baggage/evacuate search and identification."})
s2 = db.item_add(category="Station", data={"Name":"DFAT", "Index":"2", "Misc":"Identification and clearence by DFAT."})
s3 = db.item_add(category="Station", data={"Name":"Medical", "Index":"3", "Misc":"Medical services for evacuees."})
s4 = db.item_add(category="Station", data={"Name":"Clean Hold", "Index":"4", "Misc":"Waiting area for evacuees before boarding flights."})
s5 = db.item_add(category="Station", data={"Name":"Airside", "Index":"5", "Misc":"Boarding and departed flights."})
s8 = db.item_add(category="Station", data={"Name":"Missing", "Index":"8", "Misc":"Evacuees that are missing."})
s9 = db.item_add(category="Station", data={"Name":"Withdrawn", "Index":"9", "Misc":"Evacuees that have withdrawn from evacuation."})

for _ in range(0, 25):
    family_add()

for _ in range(0, 100):
    evacuee_add()

for id in random.sample(population=IDS, k=30):
    dest, = random.choices(population=[s1, s2, s3, s4, s5, s8, s9], weights=[20, 2, 0, 20, 6, 1, 1])
    db.container_add(container=dest, item=id)

for _ in range(0, 4):
    x = db.item_add(category="Flight", data={"Aircraft Type": "C-17 Globemaster", "Flight Number": f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1,9999):04d}", "Flight Date":"06/09/2021", "Departure Time":str(random.randint(12,20)*100), "Capacity (KG)":"40000"})
    db.container_add(container=s5, item=x)

sys.exit(0)
