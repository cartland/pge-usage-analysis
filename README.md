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

       MONTH COST 2020  USAGE 2020 COST 2021  USAGE 2021 COST 2022   USAGE 2022 COST 2023   USAGE 2023 COST 2024   USAGE 2024
           1    $53.44  219.56 kWh   $170.08  614.12 kWh     $0.00   634.84 kWh     $0.00    61.26 kWh    $89.86   177.40 kWh
           2    $49.40  200.36 kWh   $153.52  556.20 kWh     $0.00   595.64 kWh     $0.00  -100.65 kWh   $-16.67   -61.36 kWh
           3   $137.28  516.48 kWh   $181.96  634.00 kWh     $0.00    73.00 kWh     $0.00  -224.02 kWh  $-119.75  -305.07 kWh
           4   $179.79  657.64 kWh   $154.28  539.28 kWh     $0.00  -533.14 kWh     $0.00  -665.92 kWh   $-72.03  -194.75 kWh
           5   $205.09  721.76 kWh   $110.88  390.04 kWh     $0.00  -699.61 kWh     $0.00  -658.55 kWh  $-280.69  -664.41 kWh
           6   $167.74  584.96 kWh   $116.72  413.36 kWh     $0.00  -714.01 kWh     $0.00  -779.09 kWh  $-300.86  -710.91 kWh
           7    $15.64   63.64 kWh   $119.88  419.32 kWh     $0.00  -657.43 kWh     $0.00  -709.36 kWh  $-236.22  -624.73 kWh
           8   $195.06  676.96 kWh   $134.12  463.84 kWh     $0.00  -479.34 kWh     $0.00  -701.32 kWh  $-176.04  -480.99 kWh
           9   $113.36  408.60 kWh   $203.96  693.76 kWh     $0.00  -282.11 kWh     $0.00  -299.67 kWh   $-84.02  -265.44 kWh
          10   $191.83  687.12 kWh   $184.08  639.28 kWh     $0.00    73.75 kWh     $0.00  -196.41 kWh    $69.25   124.30 kWh
          11   $165.24  575.96 kWh   $127.04  430.60 kWh     $0.00   146.26 kWh     $0.00    10.62 kWh   $185.37   402.42 kWh
          12   $148.63  534.92 kWh   $176.00  605.08 kWh     $0.00   294.70 kWh     $0.00   173.10 kWh   $263.71   585.98 kWh
Yearly Total  $1622.50 5847.96 kWh  $1832.52 6398.88 kWh     $0.00 -1547.45 kWh     $0.00 -4090.01 kWh  $-678.09 -2017.56 kWh



*** NATURAL GAS USAGE ***

       MONTH COST 2020    USAGE 2020 COST 2021    USAGE 2021 COST 2022    USAGE 2022 COST 2023    USAGE 2023 COST 2024    USAGE 2024
           1    $64.12  42.98 therms    $66.43  39.94 therms    $85.60  38.90 therms    $97.41  34.93 therms    $77.61  32.51 therms
           2    $45.01  30.38 therms    $52.28  31.51 therms    $61.75  28.35 therms   $153.64  51.60 therms    $68.68  36.96 therms
           3    $50.92  33.50 therms    $74.67  44.11 therms    $49.53  24.15 therms   $115.31  50.10 therms    $26.39  29.39 therms
           4    $41.18  26.19 therms    $70.02  39.77 therms    $55.19  26.03 therms    $66.09  35.39 therms     $0.00  35.42 therms
           5       N/A           N/A    $69.05  39.73 therms    $66.01  29.25 therms    $36.77  21.93 therms     $0.00  45.59 therms
           6    $23.48  16.60 therms    $30.49  19.82 therms    $45.59  20.55 therms    $25.99  15.63 therms     $0.00  29.37 therms
           7    $26.68  18.72 therms    $28.13  18.93 therms    $34.04  15.74 therms    $32.69  18.85 therms     $0.00   5.25 therms
           8    $21.30  14.69 therms    $20.41  13.65 therms    $26.26  12.60 therms    $20.30  11.55 therms     $0.00   2.12 therms
           9    $14.96   9.44 therms    $25.22  14.72 therms    $31.29  13.81 therms    $28.25  14.61 therms     $0.00   3.16 therms
          10    $25.83  16.64 therms    $32.74  16.74 therms    $34.86  14.67 therms    $45.03  20.80 therms     $0.00   3.13 therms
          11    $54.85  33.56 therms    $56.33  27.07 therms   $108.64  45.15 therms    $56.72  26.07 therms     $5.22   3.11 therms
          12    $81.88  49.32 therms   $133.32  62.06 therms   $126.64  51.78 therms   $104.36  44.11 therms     $5.42   2.09 therms
Yearly Total   $450.21 292.02 therms   $659.09 368.05 therms   $725.40 320.98 therms   $782.56 345.57 therms   $183.32 228.10 therms
```
