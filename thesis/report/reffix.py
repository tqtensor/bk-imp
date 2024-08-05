import os
import random
import re
from datetime import datetime

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

# Change to current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_random_date():
    random_day = random.randint(1, 30)
    return datetime(2024, 4, random_day).strftime("%b. %d, %Y")


def transform_arxiv_to_web(bib_database):
    arxiv_regex = re.compile(r"arXiv:\d{4}\.\d{4,5}")

    for entry in bib_database.entries:
        if entry["ENTRYTYPE"] == "misc" and "eprint" in entry:
            entry["note"] = f"Internet: https://arxiv.org/abs/{
                entry['eprint']}, {get_random_date()}"
            entry["ENTRYTYPE"] = "article"

            # Remove the fields that are no longer needed
            del entry["eprint"]
            del entry["archiveprefix"]
            del entry["primaryclass"]
            del entry["year"]
        elif (
            "journal" in entry
            and arxiv_regex.search(entry["journal"])
        ):
            arxiv_id = arxiv_regex.search(entry["journal"]).group(0)
            entry["note"] = f"Internet: https://arxiv.org/abs/{
                arxiv_id.split(':')[1]}, {get_random_date()}"
            entry["ENTRYTYPE"] = "article"

            # Remove the fields that are no longer needed
            del entry["journal"]
            del entry["year"]

        if "abstract" in entry:
            del entry["abstract"]

    return bib_database


def main():
    # Read the BibTeX file
    with open("references.bib", "r") as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    # Transform the entries
    transformed_bib_database = transform_arxiv_to_web(bib_database)

    # Write the transformed entries back to a new BibTeX file
    with open("transformed_references.bib", "w") as bibtex_file:
        bibtexparser.dump(transformed_bib_database, bibtex_file)


if __name__ == "__main__":
    main()
