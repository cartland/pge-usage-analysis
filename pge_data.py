import pandas as pd
import glob
import os
import re

class PGEData:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def find_skiprows(csv_file):
        """
        Finds the number of rows to skip in a CSV file by looking for the row starting with "TYPE".

        Args:
            csv_file: The path to the CSV file.

        Returns:
            The number of rows to skip.
        """
        skiprows = 0
        with open(csv_file, 'r') as f:
            for line in f:
                if line.startswith("TYPE"):
                    return skiprows
                skiprows += 1
        return skiprows  # Return the last value of skiprows if "TYPE" is not found

    @staticmethod
    def load_directory(directory_name, recursive=True):
        """Loads all CSV files in a directory into a single DataFrame.

        Args:
            directory_name: The name of the directory.
            recursive: Whether to search subdirectories recursively.

        Returns:
            A PGEData object containing the combined data.
        """
        if recursive:
            filepaths = glob.glob(os.path.join(directory_name, '**/*.csv'), recursive=True)
        else:
            filepaths = glob.glob(os.path.join(directory_name, '*.csv'))

        dfs = []
        for filepath in filepaths:
            try:
                skiprows = PGEData.find_skiprows(filepath)
                df = pd.read_csv(filepath, skiprows=skiprows)

                # Calculate net usage (IMPORT - EXPORT)
                if 'IMPORT (kWh)' in df.columns and 'EXPORT (kWh)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['IMPORT (kWh)'], errors='coerce') - \
                                  pd.to_numeric(df['EXPORT (kWh)'], errors='coerce')
                    df['UNITS'] = 'kWh'  # Set unit to kWh for net usage
                elif 'USAGE (kWh)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['USAGE (kWh)'], errors='coerce')
                    df['UNITS'] = 'kWh'  # Set unit to kWh if not present
                elif 'USAGE (therms)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['USAGE (therms)'], errors='coerce')
                    df['UNITS'] = 'therms'  # Set unit to therms if not present
                elif 'USAGE' in df.columns and 'UNITS' in df.columns:
                    # Use existing UNITS if already present
                    df['USAGE'] = pd.to_numeric(df['USAGE'], errors='coerce')
                else:
                    # If no relevant columns are found
                    print(f"Warning: No usage data found in {filepath}")
                    continue

                # Parse COST correctly
                if 'COST' in df.columns:
                    df['COST'] = pd.to_numeric(df['COST'].astype(str).replace(r'[$,]', '', regex=True), errors='coerce')

                dfs.append(df)
            except FileNotFoundError:
                print(f"Warning: File not found: {filepath}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True, sort=False)
            return PGEData(combined_df)
        else:
            return None

    def filter(self, filter_func):
        """Filters the data based on a filter function.

        Args:
            filter_func: A function that takes a DataFrame and returns a filtered DataFrame.

        Returns:
            A new PGEData object with the filtered data.
        """
        return PGEData(filter_func(self.df))

    def add_column(self, column_name, apply_func):
        """Adds a new column to the data.

        Args:
            column_name: The name of the new column.
            apply_func: A function that takes a row and returns the value for the new column.

        Returns:
            A new PGEData object with the added column.
        """
        new_df = self.df.copy()
        new_df[column_name] = new_df.apply(lambda row: apply_func(row), axis=1)
        return PGEData(new_df)

    def group(self, group_by_column, aggregation_func):
        """Groups the data by a column and applies an aggregation function.

        Args:
            group_by_column: The column to group by.
            aggregation_func: A function that takes a group and returns a dictionary of aggregated values.

        Returns:
            A new PGEData object with the grouped data.
        """
        # Reset index if necessary and then apply grouping
        new_df = self.df.copy()
        if new_df.index.name != group_by_column:
            new_df = new_df.reset_index()
        grouped = new_df.groupby(group_by_column).apply(aggregation_func).reset_index()
        return PGEData(grouped)

    def __iter__(self):
        """Makes the PGEData object iterable, returning (column, value) pairs."""
        for row in self.df.itertuples(index=False):
            yield row

class Filter:
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value

    def __call__(self, df):
        """Applies the filter to a DataFrame."""
        if self.operator == "contains":
            # Case-insensitive 'contains'
            return df[df[self.column].str.lower().str.contains(str(self.value).lower(), na=False)]
        elif self.operator == "equals":
            # Convert to the same type for comparison
            return df[df[self.column].astype(str) == str(self.value)]
        elif self.operator == "greater_than":
            return df[df[self.column] > self.value]
        elif self.operator == "less_than":
            return df[df[self.column] < self.value]
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

def display_summary(data):
    """
    Displays a formatted summary of the PGE data, separated by year and usage type.

    Args:
        data: A PGEData object containing the usage data.
    """

    if data is None or data.df.empty:
        print("No data to display.")
        return

    # Convert 'DATE' to datetime objects
    data.df['DATE'] = pd.to_datetime(data.df['DATE'])

    # Add 'YEAR', 'MONTH', and 'USAGE_TYPE' columns
    data.df['YEAR'] = data.df['DATE'].dt.year
    data.df['MONTH'] = data.df['DATE'].dt.month
    data.df['USAGE_TYPE'] = data.df['TYPE'].apply(lambda x: 'Electric usage' if 'Electric usage' in str(x) else 'Natural gas usage' if 'Natural gas usage' in str(x) else None)

    # Get unique years and usage types
    years = sorted(data.df['YEAR'].unique())
    usage_types = ["Electric usage", "Natural gas usage"]

    for usage_type in usage_types:
        print(f"\n*** {usage_type.upper()} ***\n")

        # Filter data for the current usage type
        type_data = data.df[data.df['USAGE_TYPE'] == usage_type]

        if type_data.empty:
            print("No data available.\n")
            continue

        # Create a pivot table for the current usage type
        pivot_table = pd.pivot_table(
            type_data,
            values=['USAGE', 'COST'],
            index=['MONTH'],
            columns=['YEAR'],
            aggfunc={'USAGE': 'sum', 'COST': 'sum'},
            fill_value=None
        )

        # Calculate yearly totals and add them as a row
        yearly_totals = type_data.groupby('YEAR').agg({'USAGE': 'sum', 'COST': 'sum'})
        yearly_totals['MONTH'] = 'Yearly Total'
        yearly_totals = yearly_totals.set_index('MONTH')
        pivot_table = pd.concat([pivot_table, yearly_totals])

        # Flatten MultiIndex columns and format the values
        pivot_table.columns = [f'{col[0]} {col[1]}' for col in pivot_table.columns.values]
        
        # Ensure all months are represented
        all_months = pd.DataFrame({'MONTH': range(1, 13)})
        all_months['MONTH'] = all_months['MONTH'].astype(str)
        pivot_table.reset_index(inplace=True)
        pivot_table['MONTH'] = pivot_table['MONTH'].astype(str)
        pivot_table = pd.merge(all_months, pivot_table, on='MONTH', how='outer')

        # Reorder columns to have years in ascending order
        year_cols = [col for col in pivot_table.columns if 'USAGE' in col or 'COST' in col]
        year_cols.sort(key=lambda x: int(x.split()[-1]))  # Sort by year numerically
        pivot_table = pivot_table[['MONTH'] + year_cols]

        # Format the values in the pivot table after merging
        for col in pivot_table.columns:
            if 'USAGE' in col:
                unit = type_data['UNITS'].dropna().iloc[0] if not type_data['UNITS'].dropna().empty else 'N/A'
                pivot_table[col] = pivot_table[col].apply(lambda x: f"{x:.2f} {unit}" if pd.notna(x) else "N/A")
            elif 'COST' in col:
                pivot_table[col] = pivot_table[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")

        # Display the pivot table
        print(pivot_table.to_string(index=False))
        print("\n")

# Example usage:
if __name__ == "__main__":
    data = PGEData.load_directory('pge_data', recursive=True)

    if data is None:
        print("No data loaded.")
    else:
        display_summary(data)
