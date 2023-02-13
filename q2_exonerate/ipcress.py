# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from q2_types.feature_data import DNAFASTAFormat


def simulate_pcr(
        templates: DNAFASTAFormat, experiments: pd.DataFrame
) -> DNAFASTAFormat:
    return DNAFASTAFormat()
