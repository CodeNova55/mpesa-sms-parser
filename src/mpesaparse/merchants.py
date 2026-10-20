import random

# All merchant names here are invented.
CATEGORY_WORDS = {
    "groceries": ["SUPERMARKET", "MINIMART", "GROCERS", "BUTCHERY", "FRESH PRODUCE", "WHOLESALERS", "GROCERY STORE", "DAIRY"],
    "transport": ["PETROL STATION", "FUEL STATION", "MATATU SACCO", "CABS", "TAXI SERVICES", "PARKING", "BUS SERVICES", "MOTORS"],
    "utilities": ["ELECTRICITY PREPAID", "WATER AND SEWERAGE", "INTERNET SERVICES", "FIBRE", "GAS REFILL", "POWER TOKENS", "TV SUBSCRIPTIONS", "WATER COMPANY"],
    "eating_out": ["RESTAURANT", "CAFE", "KITCHEN", "GRILL", "PIZZA", "BAKERY", "JUICE BAR", "NYAMA CHOMA"],
    "health": ["PHARMACY", "CHEMIST", "CLINIC", "HOSPITAL", "DENTAL CARE", "MEDICAL CENTRE", "OPTICALS", "LABORATORY"],
    "education": ["SCHOOL", "ACADEMY", "COLLEGE", "UNIVERSITY", "TUITION CENTRE", "SCHOOL FEES", "BOOKSHOP", "INSTITUTE"],
    "shopping": ["BOUTIQUE", "ELECTRONICS", "HARDWARE", "FASHION", "SHOES", "FURNITURE", "COSMETICS", "PHONES AND ACCESSORIES"],
    "other": ["ENTERPRISES", "TRADERS", "AGENCIES", "HOLDINGS", "VENTURES", "SOLUTIONS", "GENERAL SUPPLIES", "INVESTMENTS"],
}

FIRST_WORDS = [
    "SUNRISE", "MOUNTAIN", "LAKESIDE", "GOLDEN", "BLUE", "UMOJA", "TUMAINI", "BARAKA",
    "NYOTA", "PAMOJA", "KILIMANI", "WESTLANDS", "ELITE", "PRIME", "HARAMBEE", "ZURI",
    "JUA", "SAVANNA", "RIFT", "CORAL",
]

ENDINGS = ["", "", "", " LTD", " LIMITED", " CO", " BRANCH 2", " PLAZA"]


def _with_typo(name, rng):
    """Drop one letter in about 15 percent of names, like a real typo."""
    if len(name) < 6 or rng.random() > 0.15:
        return name
    i = rng.randrange(1, len(name) - 1)
    return name[:i] + name[i + 1:]


def generate_merchants(n_per_category=150, seed=42):
    """Make labelled merchant names for training. Returns (names, labels)."""
    rng = random.Random(seed)
    names = []
    labels = []
    for category, words in CATEGORY_WORDS.items():
        for _ in range(n_per_category):
            name = rng.choice(FIRST_WORDS) + " " + rng.choice(words) + rng.choice(ENDINGS)
            names.append(_with_typo(name, rng))
            labels.append(category)
    return names, labels
