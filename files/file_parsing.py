
import pandas as pd
import re
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import (Literal, Optional)
from dataclasses import dataclass, field
from typing import Union, Any


@dataclass
class FileParserConfig:
    header_row: Optional[int] = 0
    skip_footer: Optional[int] = 0
    skip_rows: Optional[int] = 0
    tab_pattern: Optional[str] = None
    engine: Literal['openpyxl', 'xlrd'] = 'openpyxl'

    def __post_init__(self):
        self.skip_footer = max(0, self.skip_footer or 0)
        self.skip_rows = max(0, self.skip_rows or 0)
        if self.header_row is not None:
            self.header_row = max(0, self.header_row)


class FileParser:
    def __init__(self, file_obj: Union[str, InMemoryUploadedFile], config: FileParserConfig):
        self.file_obj = file_obj
        self.config = config
        self.raw_data = None
        self.data = None

    def process_xlsx(self):
        self.raw_data = self._read_excel(read_header=False)
        sheets = self._read_excel(read_header=True)
        filtered = self._filter_sheets(sheets)
        self.data = pd.concat(filtered.values(), ignore_index=True)

    def process_csv(self):
        stream = self._get_csv_stream()
        self.raw_data = pd.read_csv(stream)
        stream.seek(0)
        self.data = pd.read_csv(
            stream,
            skiprows=self.config.skip_rows or 0,
            skipfooter=self.config.skip_footer or 0,
            engine='python'
        )

    def process_html(self, data_index_number=0):
        content = self._get_html_content()
        self.raw_data = pd.read_html(content)
        df = self.raw_data[data_index_number]

        if self.config.header_row is not None:
            df.columns = df.iloc[self.config.header_row]
            df = df.iloc[self.config.header_row + 1:]

        if self.config.skip_footer:
            df = df.iloc[:-self.config.skip_footer]

        self.data = df.reset_index(drop=True)

    def _read_excel(self, read_header=True):
        header = self.config.header_row if read_header else None
        stream = self._get_excel_stream()
        return pd.read_excel(
            stream,
            header=header,
            sheet_name=None,
            engine=self.config.engine,
            skipfooter=self.config.skip_footer or 0,
        )

    def _get_excel_stream(self):
        if isinstance(self.file_obj, str):
            return self.file_obj
        content = self.file_obj.read()
        self.file_obj.seek(0)
        return io.BytesIO(content)

    def _get_csv_stream(self):
        if isinstance(self.file_obj, str):
            return open(self.file_obj, 'r')
        content = self.file_obj.read().decode('utf-8')
        self.file_obj.seek(0)
        return io.StringIO(content)

    def _get_html_content(self):
        if isinstance(self.file_obj, str):
            return self.file_obj
        content = self.file_obj.read().decode('utf-8')
        self.file_obj.seek(0)
        return io.StringIO(content)

    def _filter_sheets(self, dfs):
        if self.config.tab_pattern:
            dfs = {k: v for k, v in dfs.items() if re.match(self.config.tab_pattern, k)}
            for name, df in dfs.items():
                df['sheet_name'] = name
        return dfs



# ------------------------------------------------------------------------------
# Standalone utility functions
# ------------------------------------------------------------------------------

def clean_columns(data: pd.DataFrame) -> pd.DataFrame:
    data.columns = [col.replace('\n', ' ') for col in data.columns]
    return data

def filter_data(data: pd.DataFrame, query: str) -> pd.DataFrame:
    return data.query(query)

def drop_cols(data: pd.DataFrame, col_list) -> pd.DataFrame:
    return data.drop(col_list, axis=1)

def drop_cols_by_name(data: pd.DataFrame, pattern) -> pd.DataFrame:
    cols = [col for col in data.columns if re.match(pattern, col)]
    return drop_cols(data, cols)

def column_fill(data: pd.DataFrame, column: str, new_column=None, query_filter=None) -> pd.DataFrame:
    new_column = new_column or column
    if query_filter:
        idx = data.query(query_filter).index
        data.loc[idx, new_column] = data.loc[idx, column]
        data[new_column] = data[new_column].ffill()
    else:
        data[new_column] = data[column].ffill()
    return data


# ------------------------------------------------------------------------------
# ParsePipeline class
# ------------------------------------------------------------------------------

class ParsePipeline:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def clean_columns(self):
        self.df = clean_columns(self.df)
        return self

    def add_defaults(self):
        for col in ['limit', 'balance']:
            if col not in self.df:
                self.df[col] = 0
        return self

    def cast_types(self):
        if 'account_code' in self.df.columns:
            self.df['account_code'] = self.df['account_code'].astype(str)
        return self

    def filter_rows(self, query: str):
        self.df = filter_data(self.df, query)
        return self

    def replace_column_where(self, condition, source_col: str, target_col: str):
        self.df.loc[condition, target_col] = self.df.loc[condition, source_col]
        return self

    def drop_by_name(self, pattern: str):
        self.df = drop_cols_by_name(self.df, pattern)
        return self

    def fill_column(self, source: str, target=None, query_filter=None):
        self.df = column_fill(self.df, column=source, new_column=target, query_filter=query_filter)
        return self

    def standardise(self, column_mapping:dict, required_columns:dict):
        self._validate()
        self.df = self.df.rename(columns=column_mapping)
        for col, dtype in required_columns.items():
            if col not in self.df.columns:
                self.df[col] = pd.Series([None] * len(self.df), dtype=dtype)
            if dtype == str:
                self.df[col] = self.df[col].str.replace('\.0', '', regex=True)

        self.df = self.df.astype({col: dtype for col, dtype in required_columns.items() if col not in self.df.columns})
        self.df = self.df[list(required_columns.keys())]
        return self

    def _validate(self):
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("ParsePipeline expects a pandas DataFrame.")
        if self.df.empty:
            raise ValueError("Input DataFrame is empty.")

    def result(self):
        return self.df


