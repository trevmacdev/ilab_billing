######
# Retrieve three years of South African public holidays from Nager.Date
# Called by metadata.py to update config file as needed
######


#!/usr/bin/env python3
import sys
import datetime
import json
import urllib.request

def fetch_sa_public_holidays(year):

    base_url = "https://date.nager.at/api/v3/PublicHolidays"
    url = f"{base_url}/{year}/ZA"
    req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        return json.loads(data)

def pub_hol(year):

    years = [str(int(year) - 1), year, str(int(year) + 1)]
    holidays = []
    for y in years:
        print(f"South Africa public holidays for {y} (source: Nager.Date):")
        try:
            holidays = holidays + fetch_sa_public_holidays(y)
        except Exception as e:
            # Keep it simple: just print and exit
            print(f"Failed to fetch holidays: {e}")
            return

    # Each item typically contains:
    # date, localName, name, countryCode, fixed, global, counties, launchYear, types
    # We'll print the date and names.
    for h in holidays:
        date = h.get("date", "")
        local_name = h.get("localName", "")
        english_name = h.get("name", "")
        types = ", ".join(h.get("types", [])) if isinstance(h.get("types"), list) else ""
        print(f"- {date}: {local_name} / {english_name} [{types}]")

    
    # NEW: print a comma-separated list of date values only
    date_values = [h.get("date", "") for h in holidays]
    print("\nComma-separated date values:")
    print(",".join(date_values))
    return(",".join(date_values))


    # If you want the raw JSON, uncomment:
    # print(json.dumps(holidays, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    pub_hol()
