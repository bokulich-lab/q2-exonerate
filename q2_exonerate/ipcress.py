# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from typing import List

import pandas as pd
import skbio
from q2_types.feature_data import DNAFASTAFormat
from skbio import DNA

from q2_exonerate.types._format import IPCRessExperimentFormat
from q2_exonerate.utils import run_command


def _dump_seqs_to_file(products: List[dict]) -> DNAFASTAFormat:
    results = DNAFASTAFormat()
    with open(str(results), "a") as fin:
        for product in products:
            seq = DNA(sequence=product["sequence"], metadata={"id": product["id"]})
            skbio.io.write(seq, format="fasta", into=fin)
    return results


def _extract_pcr_meta(products: List[dict]) -> pd.DataFrame:
    meta = pd.DataFrame.from_records(products)
    meta["id"] = meta["id"].apply(lambda x: x.split(":filter")[0])
    meta["matches_fwd_frac"] = meta["matches_fwd"].apply(_calculate_match_frac)
    meta["matches_rev_frac"] = meta["matches_rev"].apply(_calculate_match_frac)
    meta.drop("sequence", axis=1, inplace=True)
    meta.set_index("id", drop=True, inplace=True)
    return meta


def _calculate_match_frac(match: str) -> float:
    match_split = match.split("/")
    return float(match_split[0]) / float(match_split[1])


def _process_one_product(line: List[str]) -> dict:
    product = {
        "experiment": line[2].split(":")[-1].strip(),
        "target": line[4].split("Target:")[-1].strip(),
        "match_orientation": line[7].split(":")[-1].strip(),
    }

    matches = line[5].lstrip().split(" ")
    if product["match_orientation"] == "revcomp":
        product.update({"matches_fwd": matches[2], "matches_rev": matches[1]})
    else:
        product.update({"matches_fwd": matches[1], "matches_rev": matches[2]})

    product_length = line[6].lstrip().split(" ")
    ranges = product_length[4][:-1].split("-")
    product.update(
        {
            "length": int(product_length[1]),
            "range_min": int(ranges[0]),
            "range_max": int(ranges[1]),
            "start_position": int(line[16].split("start")[1].strip().split(" ")[0]),
            "id": line[16].strip()[1:],
            "sequence": "",
        }
    )

    for l_ in line[17:]:
        if not l_ or "completed ipcress analysis" in l_:
            break
        product["sequence"] += l_

    return product


def _process_pcr_products(lines: List[str]) -> list:
    lines = [line.split("\n") for line in lines if "Experiment" in line]
    products = [_process_one_product(line) for line in lines]
    return products


def simulate_pcr(
    templates: DNAFASTAFormat,
    experiments: IPCRessExperimentFormat,
    seed: int = 12,
    memory: int = 32,
    mismatch: int = 0,
) -> (DNAFASTAFormat, pd.DataFrame):
    cmd = [
        "ipcress",
        "-i",
        str(experiments),
        "-s",
        str(templates),
        "-S",
        str(seed),
        "-M",
        str(memory),
        "-m",
        str(mismatch),
        "-p",
        "-P",
    ]

    out = run_command(cmd, verbose=True)
    lines = out.decode().split("Ipcress result")

    products = _process_pcr_products(lines)
    results = _dump_seqs_to_file(products)
    meta = _extract_pcr_meta(products)

    return results, meta
