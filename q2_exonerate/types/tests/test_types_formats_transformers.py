# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import qiime2
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_exonerate.types._format import (
    IPCRessExperimentDirFmt,
    IPCRessExperimentFormat,
    PCRProductMetadataDirFmt,
    PCRProductMetadataFormat,
)
from q2_exonerate.types._type import IPCRessExperiments, PCRProductMetadata


class TestFormats(TestPluginBase):
    package = "q2_exonerate.types.tests"

    def test_ipcress_fmt(self):
        exp_path = self.get_data_path("ipcress_exp.ipcress")
        format = IPCRessExperimentFormat(exp_path, mode="r")
        format.validate()

    def test_ipcress_fmt_wrong_col_count(self):
        exp_path = self.get_data_path("ipcress_exp_wrong_cols.ipcress")
        format = IPCRessExperimentFormat(exp_path, mode="r")
        with self.assertRaisesRegexp(
            ValidationError, "should have 5 columns. 6 were found."
        ):
            format.validate()

    def test_ipcress_fmt_wrong_min_len(self):
        exp_path = self.get_data_path("ipcress_exp_wrong_min.ipcress")
        format = IPCRessExperimentFormat(exp_path, mode="r")
        with self.assertRaisesRegexp(
            ValidationError, "minimum length of a PCR product cannot be negative"
        ):
            format.validate()

    def test_ipcress_fmt_wrong_max_len(self):
        exp_path = self.get_data_path("ipcress_exp_wrong_max.ipcress")
        format = IPCRessExperimentFormat(exp_path, mode="r")
        with self.assertRaisesRegexp(
            ValidationError, "maximum length of a PCR product cannot be negative"
        ):
            format.validate()

    def test_pcr_prod_meta_fmt(self):
        exp_path = self.get_data_path("pcr_prod_meta.tsv")
        format = PCRProductMetadataFormat(exp_path, mode="r")
        format.validate()

    def test_pcr_prod_meta_fmt_wrong_cols(self):
        exp_path = self.get_data_path("pcr_prod_meta_wrong_cols.tsv")
        format = PCRProductMetadataFormat(exp_path, mode="r")
        with self.assertRaisesRegexp(
            ValidationError, "'matches_rev_frac' is not a column."
        ):
            format.validate()


class TestTypes(TestPluginBase):
    package = "q2_exonerate.types.tests"

    def test_ipcress_exp_semantic_type_registration(self):
        self.assertRegisteredSemanticType(IPCRessExperiments)

    def test_pcr_prod_meta_semantic_type_registration(self):
        self.assertRegisteredSemanticType(PCRProductMetadata)

    def test_ipcress_exp_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            IPCRessExperiments, IPCRessExperimentDirFmt
        )

    def test_pcr_prod_meta_to_format_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            PCRProductMetadata, PCRProductMetadataDirFmt
        )


class TestTransformers(TestPluginBase):
    package = "q2_exonerate.types.tests"

    def setUp(self):
        super().setUp()
        ipcress_exp_path = self.get_data_path("ipcress_exp.ipcress")
        self.ipcress_exp = IPCRessExperimentFormat(ipcress_exp_path, mode="r")
        self.ipcress_exp_df = pd.read_csv(
            ipcress_exp_path, sep=" ", header=None, index_col=None
        )

        pcr_prod_path = self.get_data_path("pcr_prod_meta.tsv")
        self.pcr_prod_meta = PCRProductMetadataFormat(pcr_prod_path, mode="r")
        self.pcr_prod_meta_df = pd.read_csv(
            pcr_prod_path, sep="\t", header=0, index_col=0
        )

    def test_import_ipcress_tabulated(self):
        ipcress_exp_path = self.get_data_path("ipcress_exp_tabs.ipcress")
        ipcress_exp = IPCRessExperimentFormat(ipcress_exp_path, mode="r")
        ipcress_exp.validate()

    def test_dataframe_to_ipcress_exp(self):
        transformer = self.get_transformer(pd.DataFrame, IPCRessExperimentFormat)
        obs = transformer(self.ipcress_exp_df)
        self.assertIsInstance(obs, IPCRessExperimentFormat)

        obs = pd.read_csv(str(obs), sep=" ", header=None)
        pd.testing.assert_frame_equal(obs, self.ipcress_exp_df)

    def test_ipcress_exp_to_dataframe(self):
        _, obs = self.transform_format(
            IPCRessExperimentFormat, pd.DataFrame, "ipcress_exp.ipcress"
        )
        self.assertIsInstance(obs, pd.DataFrame)
        pd.testing.assert_frame_equal(obs, self.ipcress_exp_df)

    def test_dataframe_to_pcr_prod(self):
        transformer = self.get_transformer(pd.DataFrame, PCRProductMetadataFormat)
        obs = transformer(self.pcr_prod_meta_df)
        self.assertIsInstance(obs, PCRProductMetadataFormat)

        obs = pd.read_csv(str(obs), sep="\t", header=0, index_col=0)
        pd.testing.assert_frame_equal(obs, self.pcr_prod_meta_df)

    def test_pcr_prod_to_dataframe(self):
        _, obs = self.transform_format(
            PCRProductMetadataFormat, pd.DataFrame, "pcr_prod_meta.tsv"
        )
        self.assertIsInstance(obs, pd.DataFrame)
        pd.testing.assert_frame_equal(obs, self.pcr_prod_meta_df)

    def test_pcr_prod_to_q2_metadata(self):
        _, obs = self.transform_format(
            PCRProductMetadataFormat, qiime2.Metadata, "pcr_prod_meta.tsv"
        )
        exp = qiime2.Metadata(self.pcr_prod_meta_df)
        self.assertEqual(obs, exp)


if __name__ == "__main__":
    unittest.main()
