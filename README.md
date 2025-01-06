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

# Example Output

```sh
*** ELECTRIC USAGE ***

       MONTH COST 2023   USAGE 2023 COST 2024   USAGE 2024
           1     $0.00    61.26 kWh    $89.86   177.40 kWh
           2     $0.00  -100.65 kWh   $-16.67   -61.36 kWh
           3     $0.00  -224.02 kWh  $-119.75  -305.07 kWh
           4     $0.00  -665.92 kWh   $-72.03  -194.75 kWh
           5     $0.00  -658.55 kWh  $-280.69  -664.41 kWh
           6     $0.00  -779.09 kWh  $-300.86  -710.91 kWh
           7     $0.00  -709.36 kWh  $-236.22  -624.73 kWh
           8     $0.00  -701.32 kWh  $-176.04  -480.99 kWh
           9     $0.00  -299.67 kWh   $-84.02  -265.44 kWh
          10     $0.00  -196.41 kWh    $69.25   124.30 kWh
          11     $0.00    10.62 kWh   $185.37   402.42 kWh
          12     $0.00   173.10 kWh   $263.71   585.98 kWh
Yearly Total     $0.00 -4090.01 kWh  $-678.09 -2017.56 kWh



*** NATURAL GAS USAGE ***

       MONTH COST 2023    USAGE 2023 COST 2024    USAGE 2024
           1    $97.41  34.93 therms    $77.61  32.51 therms
           2   $153.64  51.60 therms    $68.68  36.96 therms
           3   $115.31  50.10 therms    $26.39  29.39 therms
           4    $66.09  35.39 therms     $0.00  35.42 therms
           5    $36.77  21.93 therms     $0.00  45.59 therms
           6    $25.99  15.63 therms     $0.00  29.37 therms
           7    $32.69  18.85 therms     $0.00   5.25 therms
           8    $20.30  11.55 therms     $0.00   2.12 therms
           9    $28.25  14.61 therms     $0.00   3.16 therms
          10    $45.03  20.80 therms     $0.00   3.13 therms
          11    $56.72  26.07 therms     $5.22   3.11 therms
          12   $104.36  44.11 therms     $5.42   2.09 therms
Yearly Total   $782.56 345.57 therms   $183.32 228.10 therms
```
