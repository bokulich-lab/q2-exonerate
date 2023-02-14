# ----------------------------------------------------------------------------
# Copyright (c) 2022, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
import qiime2
from qiime2 import Metadata

from ._type import PCRProductMetadata
from ..plugin_setup import plugin
from ._format import IPCRessExperimentFormat, PCRProductMetadataFormat


def _exp_fmt_to_metadata(ff):
    with ff.open() as fh:
        df = pd.read_csv(fh, sep='\t', header=0, index_col=0, dtype='str')
        return qiime2.Metadata(df)


@plugin.register_transformer
def _1(data: pd.DataFrame) -> IPCRessExperimentFormat:
    ff = IPCRessExperimentFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep=' ', header=True)
    return ff


@plugin.register_transformer
def _2(ff: IPCRessExperimentFormat) -> pd.DataFrame:
    with ff.open() as fh:
        df = pd.read_csv(fh, sep=' ', header=0, index_col=0)
        return df


@plugin.register_transformer
def _3(data: pd.DataFrame) -> PCRProductMetadataFormat:
    ff = PCRProductMetadataFormat()
    Metadata(data).save(str(ff))
    return ff


@plugin.register_transformer
def _4(ff: PCRProductMetadataFormat) -> pd.DataFrame:
    return Metadata.load(str(ff)).to_dataframe()


@plugin.register_transformer
def _5(ff: PCRProductMetadataFormat) -> Metadata:
    return Metadata.load(str(ff))
