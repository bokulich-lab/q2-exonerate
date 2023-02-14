# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
import skbio
from q2_types.feature_data import DNAFASTAFormat
from skbio import DNA

from q2_exonerate.types._format import IPCRessExperimentFormat
from q2_exonerate.utils import run_command


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
        "-p",
        "-P",
        "-S",
        str(seed),
        "-M",
        str(memory),
        "-m",
        str(mismatch),
    ]

    out = run_command(cmd, verbose=True)
    lines = out.decode().split("Ipcress result")
    lines = [line.split("\n") for line in lines if "Experiment" in line]
    products = []
    for line in lines:
        product = {
            "experiment": line[2].split(":")[-1].strip(),
            "target": line[4].split("Target:")[-1].strip(),
            "match_orientation": line[7].split(":")[-1].strip(),
        }

        matches = line[5].lstrip().split(" ")
        if product["match_orientation"] == "revcomp":
            product["matches_fwd"] = matches[2]
            product["matches_rev"] = matches[1]
        else:
            product["matches_fwd"] = matches[1]
            product["matches_rev"] = matches[2]

        product_length = line[6].lstrip().split(" ")
        product["length"] = int(product_length[1])

        ranges = product_length[4][:-1].split("-")
        product["range_min"] = int(ranges[0])
        product["range_max"] = int(ranges[1])

        product["start_position"] = int(
            line[16].split("start")[1].strip().split(" ")[0]
        )
        product["id"] = line[16].strip()[1:]
        product["sequence"] = ""
        for l in line[17:]:
            if not l or "completed ipcress analysis" in l:
                break
            product["sequence"] += l

        products.append(product)

    results = DNAFASTAFormat()
    with open(str(results), "a") as fin:
        for product in products:
            seq = DNA(sequence=product["sequence"], metadata={"id": product["id"]})
            skbio.io.write(seq, format="fasta", into=fin)

    meta = pd.DataFrame.from_records(products)
    meta["id"] = meta["id"].apply(lambda x: x.split(":filter")[0])
    meta.drop("sequence", axis=1, inplace=True)
    meta.set_index("id", drop=True, inplace=True)

    return results, meta
