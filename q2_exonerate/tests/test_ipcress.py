# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import subprocess
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
from q2_types.feature_data import DNAFASTAFormat, DNAIterator
from qiime2.plugin.testing import TestPluginBase

from q2_exonerate.ipcress import (
    _calculate_match_frac,
    _process_one_product,
    _process_pcr_products,
    _extract_pcr_meta,
    _dump_seqs_to_file,
    simulate_pcr,
)
from q2_exonerate.types._format import IPCRessExperimentFormat


class TestIPCRess(TestPluginBase):
    package = "q2_exonerate.tests"

    def setUp(self):
        super().setUp()
        with open(self.get_data_path("ipcress_out.txt"), "r") as f:
            self.ipcress_out = f.read()
        self.ipcress_lines = self.ipcress_out.split("Ipcress result")
        self.products = [
            {
                "experiment": "ITS9mun",
                "target": "NC_012867.1:filter(unmasked) Candida dubliniensis CD36 "
                "chromosome R, complete sequence",
                "match_orientation": "forward",
                "matches_fwd": "17/17",
                "matches_rev": "19/19",
                "length": 2072,
                "range_min": 500,
                "range_max": 5000,
                "start_position": 1864982,
                "id": "ITS9mun_product_1 seq NC_012867.1:filter(unmasked) start "
                "1864982 length 2072",
                "sequence": "GTACACACCGCCCGTCGCTACTACCGATTGAATGGCTTAGTGAGGCTTCAA"
                "GATTGGCGCCGCGGGAGGGGCAA",
            },
            {
                "experiment": "ITS9mun",
                "target": "NC_042506.1:filter(unmasked) Pichia kudriavzevii "
                "chromosome 1, complete sequence",
                "match_orientation": "revcomp",
                "matches_fwd": "17/17",
                "matches_rev": "19/19",
                "length": 2040,
                "range_min": 500,
                "range_max": 5000,
                "start_position": 1904,
                "id": "ITS9mun_product_2 seq NC_042506.1:filter(unmasked) start "
                "1904 length 2040",
                "sequence": "GTACACACCGCCCGTCGCTACTACCGATTGAATGGCTTAGTGAGGCTTCAA"
                "GATTGGCGCCGCGGGAG",
            },
        ]
        self.pcr_prod_df = pd.read_csv(
            self.get_data_path("pcr_prod_meta.tsv"), sep="\t", index_col=0, header=0
        )
        self.empty_products = ['-- completed ipcress analysis\n']

    def test_calculate_match_frac(self):
        obs = _calculate_match_frac("18/20")
        self.assertEqual(obs, 0.9)

    def test_process_one_product_forward(self):
        line = self.ipcress_lines[1].split("\n")
        obs = _process_one_product(line)
        self.assertDictEqual(obs, self.products[0])

    def test_process_one_product_reverse(self):
        line = self.ipcress_lines[2].split("\n")
        obs = _process_one_product(line)
        self.assertDictEqual(obs, self.products[1])

    def test_process_pcr_products(self):
        obs = _process_pcr_products(self.ipcress_lines[:3])
        self.assertListEqual(obs, self.products)

    def test_process_pcr_products_no_hits(self):
        with self.assertRaises(ValueError):
            _process_pcr_products(self.empty_products)

    def test_extract_pcr_meta(self):
        obs = _extract_pcr_meta(self.products)
        pd.testing.assert_frame_equal(obs, self.pcr_prod_df)

    def test_dump_seqs_to_file(self):
        obs = _dump_seqs_to_file(self.products)
        self.assertIsInstance(obs, DNAFASTAFormat)

        seqs = obs.view(DNAIterator)
        for i, seq in enumerate(seqs):
            self.assertEqual(
                seq.metadata["id"], self.products[i]["id"].replace(" ", "_")
            )
            self.assertEqual(str(seq), self.products[i]["sequence"])

    @patch("subprocess.run")
    def test_simulate_pcr(self, p1):
        template = DNAFASTAFormat()
        experiments = IPCRessExperimentFormat()
        p1.return_value = MagicMock(stdout=str.encode(self.ipcress_out))

        obs_results, obs_meta = simulate_pcr(template, experiments, 12, 32, 1)

        p1.assert_called_once_with(
            [
                "ipcress",
                "-i",
                str(experiments),
                "-s",
                str(template),
                "-S",
                "12",
                "-M",
                "32",
                "-m",
                "1",
                "-p",
                "-P",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIsInstance(obs_results, DNAFASTAFormat)
        self.assertIsInstance(obs_meta, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()
