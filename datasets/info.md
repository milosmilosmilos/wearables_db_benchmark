# Datasets

The generated CSV datasets are not included in this repository, as the largest files (up to 50M rows) exceed GitHub's file size limits.

Each dataset can be regenerated locally by uncommenting the corresponding parameter block for the desired size in `generator_code/config.py`, then running `generator_code/main.py`. The resulting CSV file can be imported into ClickHouse following the steps described in the Methodology section of the paper.
