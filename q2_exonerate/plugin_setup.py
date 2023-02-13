# ----------------------------------------------------------------------------
# Copyright (c) 2023, Bokulich Laboratories.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from q2_types.feature_data import (FeatureData, Sequence)
from qiime2.plugin import Citations, Plugin

from q2_exonerate import __version__
from q2_exonerate.ipcress import simulate_pcr
from q2_exonerate.types._format import IPCRessExperimentFormat, IPCRessExperimentDirFmt
from q2_exonerate.types._type import IPCRessExperiments

citations = Citations.load("citations.bib", package="q2_exonerate")

plugin = Plugin(
    name="exonerate",
    version=__version__,
    website="https://github.com/bokulich-lab/q2-exonerate",
    package="q2_exonerate",
    description="This is a template for building a new QIIME 2 plugin.",
    short_description="",
)

plugin.methods.register_function(
    function=simulate_pcr,
    inputs={
        'templates': FeatureData[Sequence],
        'experiments': IPCRessExperiments,
    },
    parameters={},
    outputs=[('products', FeatureData[Sequence]),],
    input_descriptions={
        'templates': 'The templates to simulate PCR on.',
        'experiments': 'The ipcress experimental details.',
    },
    parameter_descriptions={},
    output_descriptions={
        'products': 'The simulated PCR products.',
    },
    name='In-silico PCR using ipcress.',
    description=(
        'Simulate multiple PCR experiments using the ipcress tool and '
        'DNA templates of choice.'
    ),
    citations=[citations['slater2005']]
)

plugin.register_formats(IPCRessExperimentFormat, IPCRessExperimentDirFmt)
plugin.register_semantic_types(IPCRessExperiments)
plugin.register_semantic_type_to_format(
    IPCRessExperiments, artifact_format=IPCRessExperimentDirFmt
)

importlib.import_module('q2_exonerate.types._transformer')
