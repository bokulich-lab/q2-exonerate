# q2-exonerate
![CI](https://github.com/bokulich-lab/q2-exonerate/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/bokulich-lab/q2-exonerate/branch/main/graph/badge.svg?token=UTM4W4B1KW)](https://codecov.io/gh/bokulich-lab/q2-exonerate)

<b>q2-exonerate</b> is a <a href="https://qiime2.org/">QIIME 2</a> plugin for the [Exonerate toolkit](https://www.ebi.ac.uk/about/vertebrate-genomics/software/exonerate).

## Installation
You can install q2-exonerate using mamba in an existing QIIME 2 environment by following the steps described below.

* Make sure to start by installing [mamba](https://mamba.readthedocs.io/en/latest/index.html) in your base environment:
    ```shell
    conda install mamba -n base -c conda-forge
    ```

* Activate your QIIME 2 environment (ver 2022.8 or later, see [the official user documentation](https://docs.qiime2.org/)) and install relevant dependencies:
    ```shell
    conda activate qiime2-{ENV_VERSION}
    mamba install -c bioconda -c conda-forge exonerate
    ```
* Install q2-exonerate:
    ```shell
    pip install git+https://github.com/bokulich-lab/q2-exonerate.git
    ```
* To see that everything worked, refresh cache and check QIIME2 help:
    ```shell
    qiime dev refresh-cache
    qiime exonerate --help
    ```

## Usage
Currently, only one action is available in the plugin - `simulate-pcr` - it can be used to carry out an _in-silico_ PCR using a set of template sequences and primers of choice.

1) First, import the list of PCR experiments to run - please check the [Ipcress documentation](https://www.ebi.ac.uk/about/vertebrate-genomics/software/ipcress-manual) for information about the file format:
    ```shell
    qiime tools import \
      --type IPCRessExperiments \
      --input-path <path-to-experiment-file> \
      --output-path ipcress_exp.qza
    ```
2) Then, to simulate a PCR experiment, run the following command:
    ```shell
    qiime exonerate siulate-pcr \
      --i-experiments ipcress_exp.qza \
      --i-templates <path-to-templates> \
      --o-products pcr_products.qza  \
      --o-product-metadata pcr_metadata.qza \
      --verbose
    ```
   where:
    - `--i-experiments` is a path the the qza file generated in step 1)
    - `--i-templates` is a path to a FeatureData[Sequence] artifact containing desired PCR templates
    - `--o-products` is a path to a FeatureData[Sequence] artifact which will contain all the identified PCR product sequences
    - `--o-product-metadata` is a path to a PCRProductMetadata artifact which will contain additional information about all the identified PCR products.

3) Optionally, you can tabulate the list of PCR product metadata and display it as a QIIME2 visualization:
    ```shell
    qiime metadata tabulate \
      --m-input-file pcr_metadata.qza \
      --o-visualization pcr_metadata.qzv
    ```

## License
q2-exonerate is released under a BSD-3-Clause license. See LICENSE for more details.
