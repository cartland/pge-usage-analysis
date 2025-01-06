import pandas as pd
import glob
import os

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

                # Rename columns to a consistent format
                if 'USAGE (kWh)' in df.columns:
                  df.rename(columns={'USAGE (kWh)': 'USAGE'}, inplace=True)
                if 'IMPORT (kWh)' in df.columns:
                  df.rename(columns={'IMPORT (kWh)': 'USAGE'}, inplace=True)
                if 'USAGE (therms)' in df.columns:
                  df.rename(columns={'USAGE (therms)': 'USAGE'}, inplace=True)

                # Add a UNITS column if it doesn't exist
                if 'UNITS' not in df.columns:
                  if 'EXPORT (kWh)' in df.columns:
                    df['UNITS'] = 'kWh'
                  elif any("therms" in col.lower() for col in df.columns):
                    df['UNITS'] = 'therms'

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

# Example usage:
if __name__ == "__main__":
    # Assuming you have a directory named 'pge_data' with CSV files
    data = PGEData.load_directory('pge_data', recursive=True)

    if data is None:
        print("No data loaded.")
    else:
        # Convert 'DATE' to datetime objects for easier date manipulation
        data.df['DATE'] = pd.to_datetime(data.df['DATE'])

        # Add a 'YEAR' column
        data = data.add_column("YEAR", lambda row: row['DATE'].year)

        # Filter for "Electric usage" in 'TYPE' column
        filter_electric = Filter("TYPE", "contains", "Electric usage")
        data = data.filter(filter_electric)

        # Filter for 'YEAR' equals 2024
        filter_year = Filter("YEAR", "equals", 2024)
        data = data.filter(filter_year)

        # Convert 'USAGE' to numeric, handling potential errors
        data.df['USAGE'] = pd.to_numeric(data.df['USAGE'], errors='coerce')

        # Group by 'MONTH' and calculate the sum of 'USAGE' for each month
        temp_df = data.df.copy()
        temp_df['MONTH'] = temp_df['DATE'].dt.month
        grouped_data = temp_df.groupby('MONTH').agg({'USAGE': 'sum'}).reset_index()
        grouped_data.rename(columns={'USAGE': 'TOTAL_USAGE'}, inplace=True)

        data = PGEData(grouped_data)

        for row in data:
            print(row.MONTH, row.TOTAL_USAGE)
