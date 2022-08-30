#!/usr/bin/env python3
"""
Construct Nexus taxa blocks from tkan.txt
July 2022
"""
import csv
import string
import sys


def load_lang_file(fname):
    with open(fname) as f:
        reader = csv.DictReader(f, delimiter="\t")
        out = list()
        for row in reader: # lowercase field names
            newrow = dict()
            for k, v in row.items():
                newrow[k.lower()] = v
            out.append(newrow)
    return out


def find_taxa(rows, taxname):
    """Find all rows where `taxname` in classification field"""
    result = []
    for row in rows:
        clades = [c.lstrip() for c in row["classification"].split(",")]
        if taxname in clades:
            result.append(row["slug"])
    return taxname, result


def make_nexus_block(name_and_taxa):
    """Return properly formatted nexus block of `taxa`"""
    taxname, result = name_and_taxa
    setname = taxname.translate(str.maketrans('', '', string.punctuation))
    template = "taxset {} {};"
    return template.format(setname, " ".join(result))


def make_xml_block(name_and_taxa):
    """Return BEAST XML block with taxa"""
    raise NotImplementedError


def main():
    lang_file = sys.argv[1]
    taxnames = sys.argv[2].split(",")
    rows = load_lang_file(lang_file)
    for tax in taxnames:
        taxa = find_taxa(rows, tax)
        print(make_nexus_block(taxa))


if __name__ == "__main__":
    main()
