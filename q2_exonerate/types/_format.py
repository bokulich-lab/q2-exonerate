# ----------------------------------------------------------------------------
# Copyright (c) 2022, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from qiime2.core.exceptions import ValidationError
from qiime2.plugin import model


class IPCRessExperimentFormat(model.TextFileFormat):
    HEADER_FIELDS = [
        'experiment_id', 'primer_fwd', 'primer_rev',
        'min_length', 'max_length'
    ]

    def _validate(self):
        df = pd.read_csv(str(self), sep=' ')

        missing_cols = [
            x for x in self.HEADER_FIELDS if x not in df.columns
        ]
        if missing_cols:
            raise ValidationError(
                'Some required columns are missing from the ipcress '
                f'experiment file: {", ".join(missing_cols)}.'
            )

        if df.shape[1] > 5:
            raise ValidationError(
                'The ipcress experiment file should have 5 columns. '
                f'{df.shape[1]} were found.'
            )

        if df['min_length'].min() < 0:
            raise ValidationError(
                'The minimum length of a PCR product cannot be negative.'
            )

        if df['max_length'].min() < 0:
            raise ValidationError(
                'The maximum length of a PCR product cannot be negative.'
            )

    def _validate_(self, level):
        self._validate()


IPCRessExperimentDirFmt = model.SingleFileDirectoryFormat(
    'IPCRessExperimentDirFmt', 'experiments.ipcress', IPCRessExperimentFormat
)
