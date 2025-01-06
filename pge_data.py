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

                # Add a USAGE_UNIT column based on usage columns
                df['USAGE_UNIT'] = df.apply(lambda row: PGEData.extract_usage_unit(row), axis=1)

                # Calculate net usage (IMPORT - EXPORT)
                if 'IMPORT (kWh)' in df.columns and 'EXPORT (kWh)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['IMPORT (kWh)'], errors='coerce') - \
                                  pd.to_numeric(df['EXPORT (kWh)'], errors='coerce')
                elif 'USAGE (kWh)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['USAGE (kWh)'], errors='coerce')
                elif 'USAGE (therms)' in df.columns:
                    df['USAGE'] = pd.to_numeric(df['USAGE (therms)'], errors='coerce')
                
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
        
    @staticmethod
    def extract_usage_unit(row):
        """
        Extracts the usage unit (e.g., kWh, therms) from the row.

        Args:
            row: A row of the DataFrame.

        Returns:
            The usage unit as a string, or None if not found.
        """
        for col in row.index:
            if 'USAGE' in col or 'IMPORT' in col or 'EXPORT' in col:
                match = re.search(r"\((.*?)\)", col)
                if match:
                    return match.group(1)
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
    Displays a formatted summary of the PGE data, separated by year.

    Args:
        data: A PGEData object containing the usage data.
    """

    if data is None or data.df.empty:
        print("No data to display.")
        return

    # Convert 'DATE' to datetime objects
    data.df['DATE'] = pd.to_datetime(data.df['DATE'])

    # Add 'YEAR' and 'MONTH' columns
    data.df['YEAR'] = data.df['DATE'].dt.year
    data.df['MONTH'] = data.df['DATE'].dt.month

    # Filter for electric usage
    data = data.filter(Filter("TYPE", "contains", "Electric usage"))

    # Get unique years
    years = sorted(data.df['YEAR'].unique())

    for year in years:
        print(f"----- {year} -----")

        # Filter data for the current year
        year_data = data.df[data.df['YEAR'] == year]

        # Calculate total usage and cost for the year
        total_usage = year_data['USAGE'].sum()
        total_cost = year_data['COST'].sum()

        # Get the usage unit
        usage_unit = year_data['USAGE_UNIT'].iloc[0] if not year_data['USAGE_UNIT'].empty else ''

        print(f"Total Usage: {total_usage:.2f} {usage_unit}")
        print(f"Total Cost: ${total_cost:.2f}")

        # Prepare monthly data
        monthly_data = year_data.groupby('MONTH').agg({'USAGE': 'sum', 'COST': 'sum'}).reset_index()
        monthly_data.rename(columns={'USAGE': 'Monthly Usage', 'COST': 'Monthly Cost'}, inplace=True)

        # Ensure all months are represented
        all_months = pd.DataFrame({'MONTH': range(1, 13)})
        monthly_data = pd.merge(all_months, monthly_data, on='MONTH', how='left')

        # Display monthly data
        print("\nMonthly Usage and Cost:")
        print(monthly_data.to_string(index=False, na_rep=""))
        print("\n")

# Example usage:
if __name__ == "__main__":
    data = PGEData.load_directory('pge_data', recursive=True)

    if data is None:
        print("No data loaded.")
    else:
        display_summary(data)