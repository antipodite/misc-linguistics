#!/usr/bin/env python3
"""
Filter ABVD cognate sets for presence/absense in subgroup(s)
July 2022
"""
import csv
import sys
import pathlib

FORMOSAN = [
    "Amis_Central_350",
    "Amis_Farang_800",
    "Amis_Fataan_799",
    "Atayal_Culi_F69_Bandai_256",
    "Atayal_Culi_L04_Mayrinax_742",
    "Atayal_Culi_L04_Skikun_802",
    "Atayal_Squliq_F69_255",
    "Atayal_Squliq_L04_819",
    "Babuza_Ts82_635",
    "Basay_L04_832",
    "Basay_Tsym91_369",
    "Bunun_F69_Southern_202",
    "Bunun_Iskubun_805",
    "Bunun_Takbanuaz_804",
    "Bunun_Takituduh_L04_803",
    "Bunun_Takituduh_L88_726",
    "Favorlang_F69_257",
    "Favorlang_Ol03_831",
    "Hoanya_Ts82_636",
    "Kanakanabu_F69_203",
    "Kanakanabu_L04_825",
    "Kavalan_F69_260",
    "Kavalan_Lts_720",
    "Paiwan_Butanglu_L04_806",
    "Paiwan_Kulalao_F82_177",
    "Paiwan_Stimul_L04_807",
    "Paiwan_Tjatjigel_Egli_1328",
    "Paiwan_Tjubar_L04_808",
    "Papora_Ts82_637",
    "Pazih_F69_266",
    "Pazih_Lts_Auran_760",
    "Puyuma_Chihpen_F69_271",
    "Puyuma_Katipul_L04_811",
    "Puyuma_Lower_Pinlang_L04_810",
    "Puyuma_Nanwang_Cq_759",
    "Puyuma_Pilam_L04_809",
    "Rukai_Budai_F69_272",
    "Rukai_Budai_L04_813",
    "Rukai_Maga_L04_814",
    "Rukai_Mantauran_L04_816",
    "Rukai_Tanan_L04_812",
    "Rukai_Tona_815",
    "Saaroa_F69_273",
    "Saaroa_L04_826",
    "Saisiyat_F69_274",
    "Saisiyat_L04_Taai_818",
    "Saisiyat_L04_Tungho_817",
    "Sakizaya_801",
    "Seediq_F69_Sakura_275",
    "Seediq_L04_Hecuo_822",
    "Seediq_L04_Paran_820",
    "Seediq_L04_Toda_821",
    "Seediq_L04_Truku_823",
    "Siraya_A_1516",
    "Siraya_F69_276",
    "Siraya_Gospel_Dialect_1519",
    "Siraya_Um_Utrecht_Manuscript_Dialect_1517",
    "Taokas_Ts82_638",
    "Thao_B96_241",
    "Tsou_Duhtu_L04_824",
    "Tsou_T63_138",
]


def load(fname):
    """Load cognate data file into list of DictRows"""
    with open(fname) as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [row for row in reader if row["Loan"] == "0"]


def all_sets(rows):
    return set([r["Cognacy"].split(",") for r in rows])


def cognates_for_language(rows):
    """Go through each language and compile cognate set for that language"""
    result = {}
    for row in rows:
        language = row["Language"]
        cognates = set(row["Cognacy"].split(","))
        if language in result:
            result[language].update(cognates)
        else:
            result[language] = cognates
    return result


def subgroup_only_sets(langcognates, languages):
    result = set()
    for l in languages:
        cognates = langcognates[l]
        result.update(cognates)
    return result


def main():
    rows = load(sys.argv[1])
    langcognates = cognates_for_language(rows)
    formosan_only = subgroup_only_sets(langcognates, FORMOSAN)
    print(formosan_only)


if __name__ == "__main__":
    main()
