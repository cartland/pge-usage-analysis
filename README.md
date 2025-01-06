# pge-usage-analysis

Download data from pge.com using the "Green Button" to export data.

The PG&E website does not allow you to export more than 1 year at a time.
We recommend downloading data for each year, such as 2024-01-01 to 2024-12-31.
The script will read all data and make it avaialble to query, so it is not required
to use specific date boundaries. The script will not try to deduplicate information
that is incluced in multiple files, so for the most accurate results, make sure to
download contiguous data that does not overlap with other files.

Example data structure after unzipping from pge.com download (request CSV file format).
Note, the script will ignore non-CSV files.

```sh
├── pge_data
│   ├── DailyUsageData-2023-01-01_to_2023-12-31
│   │   ├── pge_electric_interval_data_1234567890_2023-01-01_to_2023-12-31.csv
│   │   ├── pge_electric_interval_data_1234567890_2023-01-01_to_2023-12-31.xlsx
│   │   └── pge_gas_interval_data_1234567890_2023-01-01_to_2023-12-31.csv
│   └── DailyUsageData-2024-01-01_to_2024-12-31
│       ├── pge_electric_usage_interval_data_Service 2_2_2024-01-01_to_2024-04-14.csv
│       ├── pge_electric_usage_interval_data_Service 2_2_2024-04-15_to_2024-12-31.csv
│       └── pge_natural_gas_usage_interval_data_Service 1_1_2024-01-01_to_2024-12-31.csv
```

# Install

```sh
pip install -r requirements.txt
```

# Usage

```sh
python pge_data.py
```
