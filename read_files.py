import pandas as pd
from pathlib import Path


class InputReader:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._df = None

    def read_file(self):
        if self._df is not None:
            return self._df

        if self.file_path.suffix == ".csv":
            self._df = pd.read_csv(self.file_path)
        elif self.file_path.suffix in [".xlsx", ".xls"]:
            self._df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format")
        return self._df

    def get_columns(self):
        return list(self.read_file().columns)

    def extract_columns(self, columns):
        df = self.read_file()

        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing Columns: {missing}")

        return df[columns]


class DataExtractor:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._df = None

    def read_file(self):
        if self._df is not None:
            return self._df

        if self.file_path.suffix == ".csv":
            self._df = pd.read_csv(self.file_path)
        elif self.file_path.suffix in [".xlsx", ".xls"]:
            self._df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format")

        return self._df

    def left_join(self, df_left, df_right, join_key):
        # df_right = self.read_file()

        # if join_key not in df_left.columns:
        #     raise ValueError(f"{join_key} not found in selected columns")
        # if join_key not in df_right.columns:
        #     raise ValueError(f"{join_key} no found in second file")
        # Skip rows with missing join keys
        # df_left = df_left.dropna(subset=[join_key])
        # df_right = df_right.dropna(subset=[join_key])
        return pd.merge(df_left, df_right, on=join_key, how="left")
