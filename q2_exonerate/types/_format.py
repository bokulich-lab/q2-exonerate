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

        # missing_cols = [
        #     x for x in self.HEADER_FIELDS if x not in df.columns
        # ]
        # if missing_cols:
        #     raise ValidationError(
        #         'Some required columns are missing from the ipcress '
        #         f'experiment file: {", ".join(missing_cols)}.'
        #     )

        if df.shape[1] > 5:
            raise ValidationError(
                'The ipcress experiment file should have 5 columns. '
                f'{df.shape[1]} were found.'
            )

        if df.iloc[:, 3].min() < 0:
            raise ValidationError(
                'The minimum length of a PCR product cannot be negative.'
            )

        if df.iloc[:, 4].min() < 0:
            raise ValidationError(
                'The maximum length of a PCR product cannot be negative.'
            )

    def _validate_(self, level):
        self._validate()


IPCRessExperimentDirFmt = model.SingleFileDirectoryFormat(
    'IPCRessExperimentDirFmt', 'experiments.ipcress', IPCRessExperimentFormat
)


class PCRProductMetadataFormat(model.TextFileFormat):
    REQUIRED_COLUMNS = {
        'experiment',
        'target',
        'match_orientation',
        'matches_rev',
        'matches_fwd',
        'length',
        'range_min',
        'range_max',
        'start_position'
    }

    def _validate_(self, level):
        with open(str(self)) as fh:
            line = fh.readline()

        if len(line.strip()) == 0:
            raise ValidationError("Failed to locate header.")

        header = set(line.strip().split('\t'))
        for column in sorted(self.REQUIRED_COLUMNS):
            if column not in header:
                raise ValidationError(f"{column} is not a column")


PCRProductMetadataDirFmt = model.SingleFileDirectoryFormat(
    'PCRProductMetadataDirFmt', 'product-metadata.tsv', PCRProductMetadataFormat
)
