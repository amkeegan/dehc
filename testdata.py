import sys
from db import Database
import random as r

# ----------------------------------------------------------------------------

SEX = ["M","F","X"]
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVXYWZ'
MALE_GIVEN = ["Oliver", "Kai", "Noah", "Jordan", "William", "Riley", "Leo", 
"Eli", "Lucas", "Louis", "Liam", "Aiden", "Jack", "Jasper", "Henry", "Austin", 
"Elijah", "Gabriel", "Thomas", "Beau", "James", "Michael", "Alexander", 
"Lincoln", "Charlie", "Flynn", "Levi", "Ali", "Theodore", "Carter", "Hudson", 
"Connor", "Jacob", "Charles", "Archie", "Sonny", "Ethan", "Spencer", 
"Harrison", "Jaxon", "Mason", "Zachary", "Hunter", "Ashton", "Isaac", "Jude", 
"Oscar", "Patrick", "Cooper", "Luke", "Lachlan", "Matthew", "Luca", "Owen", 
"George", "Isaiah", "Benjamin", "Nicholas", "Harry", "Luka", "Harvey", 
"Leonardo", "Samuel", "Christian", "Hugo", "Angus", "Max", "Marcus", "Archer", 
"Bodhi", "Sebastian", "Theo", "Arlo", "Leon", "Logan", "Asher", "Muhammad", 
"Jake", "Finn", "Axel", "Xavier", "Caleb", "Ryan", "Ryder", "Edward", "Dylan", 
"Arthur", "Dominic", "Jayden", "Ari", "Jackson", "Elias", "Joshua", "Felix", 
"Daniel", "Vincent", "Joseph", "Lennox", "Adam", "Anthony"]
FEMALE_GIVEN = ["Amelia", "Freya", "Olivia", "Maya", "Charlotte", "Bonnie", 
"Mia", "Stella", "Isla", "Luna", "Ava", "Ayla", "Chloe", "Billie", "Grace", 
"Elizabeth", "Sophia", "Mackenzie", "Zoe", "Lola", "Harper", "Eloise", "Ivy", 
"Harriet", "Isabella", "Savannah", "Ella", "Aaliyah", "Sophie", "Rose", 
"Sienna", "Piper", "Matilda", "Daisy", "Willow", "Lara", "Lily", "Millie", 
"Evelyn", "Hallie", "Mila", "Elena", "Ruby", "Ariana", "Evie", "Sarah", 
"Layla", "Sadie", "Audrey", "Anna", "Emily", "Remi", "Lucy", "Phoebe", "Aria", 
"Olive", "Hannah", "Imogen", "Hazel", "Eliana", "Georgia", "Harlow", "Zara", 
"Annabelle", "Sofia", "Molly", "Scarlett", "Bella", "Ellie", "Addison", 
"Emma", "Summer", "Frankie", "Clara", "Abigail", "Claire", "Isabelle", 
"Eliza", "Florence", "Maddison", "Eva", "Gabriella", "Violet", "Zoey", 
"Emilia", "Delilah", "Elsie", "Isabel", "Eleanor", "Charlie", "Aurora", 
"Eden", "Penelope", "Adeline", "Jasmine", "Maeve", "Poppy", "Chelsea", 
"Alice", "Maryam"]
SURNAMES = ["Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", 
"Anderson", "Johnson", "White", "Thompson", "Lee", "Martin", "Thomas", 
"Walker", "Kelly", "Young", "Harris", "King", "Ryan", "Roberts", "Hall", 
"Evans", "Davis", "Wright", "Baker", "Campbell", "Edwards", "Clark", 
"Robinson", "McDonald", "Hill", "Scott", "Clarke", "Mitchell", "Stewart", 
"Moore", "Turner", "Miller", "Green", "Watson", "Bell", "Wood", "Cooper", 
"Murphy", "Jackson", "James", "Lewis", "Allen", "Bennett", "Robertson", 
"Collins", "Cook", "Murray", "Ward", "Phillips", "O'Brien", "Nguyen", 
"Davies", "Hughes", "Morris", "Adams", "Johnston", "Parker", "Ross", "Gray", 
"Graham", "Russell", "Morgan", "Reid", "Kennedy", "Marshall", "Singh", "Cox", 
"Harrison", "Simpson", "Richardson", "Richards", "Carter", "Rogers", "Walsh", 
"Thomson", "Bailey", "Matthews", "Cameron", "Webb", "Chapman", "Stevens", 
"Ellis", "McKenzie", "Grant", "Shaw", "Hunt", "Harvey", "Butler", "Mills", 
"Price", "Pearce", "Barnes", "Henderson", "Armstrong", "Fraser", "Fisher", 
"Knight", "Hamilton", "Mason", "Hunter", "Hayes", "Ferguson", "Dunn", 
"Wallace", "Ford", "Elliott", "Foster", "Gibson", "Gordon", "Howard", "Burns", 
"O'Connor", "Jenkins", "Woods", "Palmer", "Reynolds", "Holmes", "Black", 
"Griffiths", "McLean", "Day", "Andrews", "Lloyd", "Morrison", "West", 
"Duncan", "Wang", "Sullivan", "Rose", "Chen", "Powell", "Brooks", "Dawson", 
"MacDonald", "Dixon", "Wong", "Saunders", "Watts", "Francis", "Fletcher", 
"Tran", "Rowe", "Li", "Nelson"]
NATIONALITIES = ["Argentina", "Australia", "Austria", "Belarus", "Belgium", 
"Bosnia And Herzegovina", "Bulgaria", "Canada", "Costa Rica", "Croatia", 
"Cyprus", "Czech Republic", "Denmark", "Ecuador", "Estonia", "Finland", 
"France", "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", 
"Israel", "Italy", "Japan", "Jordan", "Kuwait", "Latvia", "Lithuania", 
"Malaysia", "Mexico", "Netherlands", "New Zealand", "North Macedonia", 
"Norway", "Oman", "Panama", "Poland", "Portugal", "Puerto Rico", "Qatar", 
"Romania", "Saudi Arabia", "Serbia", "Singapore", "Slovakia", "Slovenia", 
"South Africa", "South Korea", "Spain", "Sweden", "Switzerland", "Taiwan", 
"Turkey", "Ukraine", "United Arab Emirates", "United Kingdom", 
"United States", "Uruguay"]

# ----------------------------------------------------------------------------

def evacuee_test_data(db: Database, n: int):
    for i in range(1, n+1):
        print(f"Evacuee #{i}...")
        sex, = r.choices(SEX, weights=(50,49,1))
        if sex == "M":
            name = f"{r.choice(MALE_GIVEN)}"
        elif sex == "F":
            name = f"{r.choice(FEMALE_GIVEN)}"
        else:
            name = f"{r.choice((r.choice(MALE_GIVEN),r.choice(FEMALE_GIVEN)))}"
        familyname = f"{r.choice(SURNAMES)}"
        dob = f"{r.randint(1930,2020)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}"
        passport = f"M{r.randint(0,999999999):09d}" if r.random() > 0.05 else ""
        nationality = f"Australia" if r.random() > 0.25 else r.choice(NATIONALITIES)
        homeaddress = f"{r.randint(1,99)} {r.choice(ALPHABET)} Street, {r.choice(ALPHABET)}ville"
        destaddress = homeaddress if r.random() > 0.5 else f"{r.randint(1,99)} {r.choice(ALPHABET)} Street, {r.choice(ALPHABET)}ville"
        homecontact = "".join([f"{r.randint(0,9)}" for _ in range(0,8)])
        destcontact = homecontact if homeaddress == destaddress else "".join([f"{r.randint(0,9)}" for _ in range(0,8)])
        nokname = f"{r.choice((r.choice(MALE_GIVEN),r.choice(FEMALE_GIVEN)))}"
        nokfamilyname = familyname if r.random() > 0.33 else f"{r.choice(SURNAMES)}"
        nokaddress = homeaddress if r.random() > 0.66 else f"{r.randint(1,99)} {r.choice(ALPHABET)} Street, {r.choice(ALPHABET)}ville"
        nokcontact = homecontact if homeaddress == nokaddress else "".join([f"{r.randint(0,9)}" for _ in range(0,8)])
        withnok = f"Y" if r.random() > 0.75 else f"N"
        reqmedic = f"Y" if r.random() > 0.99 else f"N"
        authrelease = f"Y" if r.random() > 0.50 else f"N"

        data = {
            "Family Name":familyname,
            "Given Name(s)":name,
            "Sex":sex,
            "Date of Birth":dob,
            "Passport Number":passport,
            "Nationality":nationality,
            "Home Address":homeaddress,
            "Destination Address":destaddress,
            "Home Contact Number":homecontact,
            "Destination Contact Number":destcontact,
            "Next Of Kin Family Name":nokfamilyname,
            "Next Of Kin Given Name":nokname,
            "Next Of Kin Address":nokaddress,
            "Next Of Kin Contact Number":nokcontact,
            "Travelling With Next Of Kin":withnok,
            "Requires Medical Attention":reqmedic,
            "Authority To Release Information":authrelease}

        id = db.doc_get_id("per-")
        db.doc_edit(data, id)

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    name, n = sys.argv
    db = Database()
    db.db_delete()
    db.db_create()
    print(f"Generating {n} evacuee records...")
    evacuee_test_data(db, int(n))
