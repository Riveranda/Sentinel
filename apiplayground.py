from json import load
from commands import Session

session = Session()
with open('json/corporations.json', 'r') as file:
    obj = load(file)
    tickers = []
    for key, value in obj.items():
        if value[2] in tickers:
            print(f"DUPLICATE: {value[2]}")
        else:
            tickers.append(value[2])

session.commit()
