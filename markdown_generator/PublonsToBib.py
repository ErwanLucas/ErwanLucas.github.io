import os
import glob
import json
import re
import requests
from pybtex.database import parse_file, BibliographyData, Entry


# Function to fetch bibliographic info from https://doi.org/
def fetch_bibtex_from_doi(doi):
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DOI {doi}: {e}")
        return None

# Function to parse the DOI from a BibTeX entry
def extract_doi_from_entry(entry):
    if "doi" in entry.fields:
        return entry.fields["doi"].strip()
    return None

# Main function to process DOIs and update the BibTeX file
def process_dois(doi_list, input_bibfile, output_bibfile):
    # Read the input BibTeX file
    bib_data = parse_file(input_bibfile)

    # Create a new BibTeX database for output
    output_bib = BibliographyData()

    for doi in doi_list:
        found = False

        # Search for the DOI in the existing BibTeX file
        for key, entry in bib_data.entries.items():
            existing_doi = extract_doi_from_entry(entry)
            if existing_doi and existing_doi.lower() == doi.lower():
                print(f"Found DOI in library: {doi}")
                output_bib.entries[key] = entry
                found = True
                break

        # If DOI is not found, fetch from the web
        if not found:
            print(f"Fetching DOI from the web: {doi}")
            bibtex_entry = fetch_bibtex_from_doi(doi)
            if bibtex_entry:
                # Parse the fetched BibTeX entry and add it to the output
                try:
                    new_entry = BibliographyData.from_string(bibtex_entry, bib_format="bibtex")
                    for key, entry in new_entry.entries.items():
                        key = str(hash(doi))
                        output_bib.entries[key] = entry
                except Exception as e:
                    print(f"Error parsing BibTeX for DOI {doi}: {e}")

    # Write the new global output BibTeX file
    with open(output_bibfile, "w") as f:
        output_bib.to_file(f)
    print(f"Updated BibTeX file written to {output_bibfile}")

    # Separate proceedings and other publications
    proceedings_bib = BibliographyData()
    pubs_bib = BibliographyData()

    for key, entry in output_bib.entries.items():
        print('%s: %s'%(entry.type, entry.fields['title']))
        if entry.type in ["proceedings", "inproceedings"]:
            proceedings_bib.entries[key] = entry
        else:
            pubs_bib.entries[key] = entry

    # Write proceedings to a separate BibTeX file
    with open("proceedings.bib", "w") as proceedings_file:
        proceedings_file.write(proceedings_bib.to_string("bibtex"))

    # Write other publications to another BibTeX file
    with open("pubs.bib", "w") as pubs_file:
        pubs_file.write(pubs_bib.to_string("bibtex"))

# Example usage
if __name__ == "__main__":
    files = list(filter(os.path.isfile, glob.glob("*.json")))
    # sort by modified time
    files.sort(key=lambda x: os.path.getmtime(x))

    print(files)

    # get last item in list
    jsonDataFile = files[-1]

    print('Using File %s'%jsonDataFile)

    # Load the JSON data from the file
    file_path = jsonDataFile

    with open(file_path, "r") as file:
        data = json.load(file)

    # Extract the DOIs from the JSON data
    dois = [publication['doi'] for publication in data['records']['publication']['list']]
    dois = [doi for doi in dois if doi != '']

    # Input BibTeX file containing existing entries

    input_bibfile = "library.bib"

    # Output BibTeX file
    output_bibfile = "updated_library.bib"

    os.system("bibtool -s -d " + input_bibfile + " proceedings.bib > " + output_bibfile)

    process_dois(dois, output_bibfile, output_bibfile)




