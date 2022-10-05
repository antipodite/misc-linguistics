#!/usr/bin/env python3.9
"""
Finding all examples in the Blust PPH reflex list which have:
- A limited geographical distribution;
and/or
- Limited subgroup distribution
August 2022
"""
import csv
import itertools
import sys
import tabulate

import geopy.distance as distance
import shapely.geometry as geometry

from cldfcatalog import Config
from pyglottolog import Glottolog
from pickle import dump, load
from pathlib import Path

MICROGROUPS = [
    "Batanic",
    "Northern Luzon",
    "Central Luzon",
    "Ati",
    "Kalamian",
    "Bilic",
    "South Mangyan",
    "Palawanic",
    "Central Philippine",
    "Manobo",
    "Danaw",
    "Subanen",
    "Sangiric",
    "Minahasan",
    "Gorontalo-Mongondow"
]

MGCODES = [
    "bata1315", # Batanic
    "nort3238", # Northern Luzon
    "nort2873", # Northern Mangyan
    "sang1335", # Sangiric
    "bili1253", # Bilic
    "cent2080", # Central Luzon
    "kala1389", # Kalamian
    "mina1272", # Minahasan
    "cent2080", # Central Luzon
    "atii1237", # Ati
    "lamp1241", # Lampungic
    "mano1276", # Manobo
    "pala1354", # Palawanic
    "goro1257", # Gorontalo/Mongondow
    "cent2246", # Central Philippine
    "suba1253", # Subanen
    "dana1253", # Danaw
    "umir1236", # Umiray Dumaget Agta
]

## The 7 most spoken languages in the Philippines according to the 2010 Philippines
## census, and major regional lingua francae cf. Ascuncion-Lande (1971)
REGIONALS = [
    "taga1270", # Tagalog
    "ilok1237", # Ilokano
    "pamp1243", # Kapampangan
    "biko1240", # Bikol (Language family. need to find out what the "prestige" language is
    "cebu1242", # Cebuano / Bisayas
    "hili1240", # Hiligaynon
    "wara1300" # Waray
]
    
class GlottoCache:
    """Save loaded Glottolog languoids so we don't have to wait every time"""
    def __init__(self, path, fname="glottocache.pickle"):
        if type(path) == str:
            path = Path(path)
        self.cachepath = path.joinpath(fname)
        try:
            with open(self.cachepath, "rb") as cachefile:
                self.cache = load(cachefile)
        except FileNotFoundError:
            self.cache = {}

        cfg = Config.from_file()
        self.glottolog = Glottolog(cfg.get_clone("glottolog"))
        # So we know whether to save
        self.written = False

    def __del__(self):
        self.save()

    def get(self, glottocode):
        if not glottocode:
            return None
        elif glottocode in self.cache:
            return self.cache[glottocode]
        else:
            lg = self.glottolog.languoid(glottocode)
            self.cache[glottocode] = lg
            self.written = True
            return lg

    def save(self):
        if self.written:
            with open(self.cachepath, "wb+") as cachefile:
                dump(self.cache, cachefile)


def load_data(path, delimiter="\t"):
    with open(path) as f:
        rows = [row for row in csv.DictReader(f, delimiter=delimiter)]
    return rows


def attach_glottolog_data(glottocache, rows):
    """Add location and subgroup data from Glottolog"""
    cache = {}
    result = []
    for row in rows:
        code = row["GlottoCode"]
        if code: # Some ACD entries don't have glottocodes
            if code not in cache:
                lg = glottocache.get(code)
                cache[code] = {"Latitude": lg.latitude,
                               "Longitude": lg.longitude,
                               "Ancestors": [a.name for a in lg.ancestors]}
            result.append(row | cache[code])
    return result


def interpolate_positions(glottocache, rows):
    """Estimate missing coordinate data.
    Some languages as referred to in the ACD are listed as families in Glottolog,
    e.g. Bikol. Treat the positions for these as the centroid of the positions
    of the member languages of the family
    """
    cache = {}
    result = []
    for row in rows:
        code = row["GlottoCode"]
        latitude = row["Latitude"]
        lg = glottocache.get(code)
        if latitude == None and lg.category == "Family":
            if code not in cache:
                lg = glottocache.get(code)
                member_coords = [(m.latitude, m.longitude) for m in lg.iter_descendants() if m.latitude]
                centroid = geometry.Polygon(member_coords).centroid
                cache[code] = centroid
            else:
                centroid = cache[code]
            try:
                row["Latitude"] = centroid.x
                row["Longitude"] = centroid.y
                row["InterpolatedDistance"] = True    
            except IndexError:
                print(row["GlottologName"], centroid.wkt)
        else:
            row["InterpolatedDistance"] = False
        result.append(row)
    return result


def groupby(rows, field):
    """Group rows according to field value. Returns {field_value: rows} dict"""
    grouped = {}
    for row in rows:
        protoform = row["ProtoForm"]
        if protoform in grouped:
            grouped[protoform].append(row)
        else:
            grouped[protoform] = [row]
    return grouped


def compute_distances(rows):
    """Calculate summary statistics for distances between languages which have
    reflexes of this cognate set
    """
    coords = [(row["Latitude"], row["Longitude"]) for row in rows] # geopy.distance.distance wants latitude first
    # Distance between each pair of languages
    distances = []
    for a, b in itertools.product(coords, repeat=2):
        try:
            if a != b:
                km = distance.distance(a, b).km
                distances.append(km)
        except ValueError:
            print("Couldn't calculate distance for {}, {}".format(a, b))
    return set(distances)


def get_unique_microgroups(glottocache, groups, rows, attr="glottocode"):
    """Count unique subgroups for this cognate set"""
    microgroups = []
    for row in rows:
        lg = glottocache.get(row["GlottoCode"])
        ancestors = [getattr(a, attr) for a in lg.ancestors]
        for group in groups:
            if group in ancestors:
                microgroups.append(group)
    return set(microgroups)


def summarise_lexical_data(glottocache, grouped):
    """Search for subgroup or geographically limited cognate sets.
    Instead of using an arbitrary distance cutoff, calculate the maximum distance
    between reflexes within a set.
    """
    result = []
    for protoform, rows in grouped.items():
        if len(rows) > 1:
            # Distances
            distances = compute_distances(rows)
            unique_groups = get_unique_microgroups(glottocache, MICROGROUPS, rows, attr="name")
            set_row = {
                "protoform": protoform,
                "reflexes": len(rows),
                "maxdist": max(distances),
                "mindist": min(distances),
                "meandist": sum(distances) / len(distances),
                "interpolated": True if any([row["InterpolatedDistance"] for row in rows]) else False,
                "microgroups": unique_groups,
                "nmicrogroups": len(unique_groups),
                "hasregionallang": has_languages(REGIONALS, rows)
            }
            result.append(set_row)
    return result


def has_languages(languages, rows):
    """Utility function to add a column for languages of interest e.g. linguas franca"""
    return bool(len([r for r in rows if r["GlottoCode"] in languages]))

##
## Clustering analysis: attempting to confirm Zorc's (2021) interaction axes by
## applying a clustering algorithm to the ACD Philippines data. Try several different
## algorithms from scikit-learn and see which gives the best results
## September 2022
##

import sklearn.cluster as skcluster
import gower


def build_microgroup_matrix(rows):
    """Transform the result of find_suspicious_sets into a presence/absence
    matrix with one column per microgroup
    """
    matrix = []
    for row in rows:
        matrix_row = {"protoform": row["protoform"], "meandist": row["meandist"]}
        for mg in MICROGROUPS:
            state = 1 if mg in row["microgroups"] else 0
            matrix_row[mg] = state
        matrix.append(matrix_row)
    return matrix


def main():
    gc = GlottoCache(".")
    infile, summaryfile, matrixfile = sys.argv[1:]
    data = load_data(infile)
    rows = attach_glottolog_data(gc, data)
    rows = interpolate_positions(gc, rows)
    grouped = groupby(rows, "Protoform")
    summary = summarise_lexical_data(gc, grouped)
    matrix = build_microgroup_matrix(summary)

    with open(summaryfile, "w") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(summary)
    with open(matrixfile, "w") as f:
        writer = csv.DictWriter(f, fieldnames=matrix[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(matrix)
    

if __name__ == "__main__":
    main()

