
import pandas as pd
import re
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import (Literal)
"""
file_parsing.py
Generic module for extracting and manipulating dataframes from various file types using pandas. 

"""


class FileBase:

    def __init__(self, fp):
        self._data = None
        self._raw_data = None
        self._header_row = None
        self._skip_footer = None
        self._skip_rows = None
        self._fp = fp

    @property
    def header_row(self):
        return self._header_row

    @header_row.setter
    def header_row(self, number):
        self._header_row = number

    @property
    def skip_footer(self):
        return self._skip_footer

    @skip_footer.setter
    def skip_footer(self, number):
        # skip_footer value is used to filter dataframe based on pandas .iloc
        self._skip_footer = number

    @property
    def skip_rows(self):
        return self._skip_rows

    @skip_rows.setter
    def skip_rows(self, number):
        self._skip_rows = number

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, df):
        self._data = df

    def process_xlsx(self, tab_pattern: str, engine:Literal['openpyxl','xlrd']='openpyxl'):
        if isinstance(self._fp, str):
            self._raw_data = pd.read_excel(
                self._fp,
                sheet_name=None,
                engine=engine,
                skipfooter=self._skip_footer,
            )
            dfs = pd.read_excel(
                self._fp,
                header=self.header_row,
                sheet_name=None,
                engine=engine,
                skipfooter=self._skip_footer,
            )
        else: # InMemoryUploadedFile
            file_bytes = self._fp.read()
            excel_io = io.BytesIO(file_bytes)
            self._raw_data = pd.read_excel(
                excel_io,
                sheet_name=None,
                engine=engine,
                skipfooter=self._skip_footer,
            )
            excel_io.seek(0)
            dfs = pd.read_excel(
                excel_io,
                header=self.header_row,
                sheet_name=None,
                engine=engine,
                skipfooter=self._skip_footer,
            )
            excel_io.seek(0)  # Reset file pointer after reading
        # regex pattern to determine which dataframe(s) in the list of dataframes
        # should be included in the final data
        # tab name is included in the final dataframe under column 'tab_name'
        if tab_pattern:
            dfs = {k: v for k, v in dfs.items() if re.match(tab_pattern, k)}
            for k, df in dfs.items():
                df['tab_name'] = k
        self.data = pd.concat([v for v in dfs.values()])

    def process_csv(self):
        if isinstance(self._fp, str):
            self._raw_data = pd.read_csv(self._fp)
            df = pd.read_csv(self._fp, skiprows=self.skip_rows, skipfooter=self.skip_footer)
        elif isinstance(self._fp, InMemoryUploadedFile):
            content = self._fp.read().decode('utf-8')  # Read file content
            self._raw_data = pd.read_csv(io.StringIO(content))
            df = pd.read_csv(io.StringIO(content), skiprows=self.skip_rows, skipfooter=self.skip_footer)
            self._fp.seek(0)  # Reset file pointer after reading
        else:
            self._raw_data = pd.read_csv(io.StringIO(self._fp.read().decode('utf-8')))
            df = pd.read_csv(io.StringIO(self._fp.read().decode('utf-8')),
                             skiprows=self.skip_rows, skipfooter=self.skip_footer)
        self.data = df

    def process_html(self, data_index_number=0):
        if isinstance(self._fp, str):
            self._raw_data = pd.read_html(self._fp)
            df = self._raw_data[data_index_number]
        elif isinstance(self._fp, InMemoryUploadedFile):
            content = self._fp.read().decode('utf-8')  # Read file content
            self._raw_data = pd.read_html(io.StringIO(content))
            df = pd.read_html(io.StringIO(content))[data_index_number]
            self._fp.seek(0)  # Reset file pointer after reading
        else:
            self._raw_data = pd.read_html(io.StringIO(self._fp.read().decode('utf-8')))
            df = pd.read_html(io.StringIO(self._fp.read().decode('utf-8')))[data_index_number]
        if self.header_row is not None:
            df.columns = df.iloc[self.header_row]
            df = df.iloc[self.header_row+1:]
        if self.skip_footer is not None:
            df = df.iloc[:self.skip_footer]
        self.data = df

    def clean_columns(self):
        assert self.data
        cols = []
        for col in self.data.columns:
            cols.append(col.replace('\n', ' '))
        self.data.columns = cols

"""
***************************************************************************************
Generic Data Processing Functions
The below functions are used for manipulating the dataframe input (UploadedFileBase.data)
***************************************************************************************
"""


def clean_columns(data: pd.DataFrame) -> pd.DataFrame:
    cols = []
    for col in data.columns:
        cols.append(col.replace('\n', ' '))
    data.columns = cols
    return data


def filter_data(data: pd.DataFrame, query: str) -> pd.DataFrame:
    return data.query(query)


def drop_cols(data: pd.DataFrame, col_list) -> pd.DataFrame:
    return data.drop(col_list, axis=1)


def drop_cols_by_name(data: pd.DataFrame, pattern) -> pd.DataFrame:
    cols = [col for col in data.columns if re.match(pattern, col)]
    return drop_cols(data, cols)


def column_fill(data: pd.DataFrame, column: str , new_column=None, query_filter=None) -> pd.DataFrame:
    if new_column is None:
        new_column = column
    if query_filter is not None:
        data.loc[data.query(query_filter).index, new_column] = \
            data.loc[data.query(query_filter).index, column]
        data[new_column] = data[new_column].ffill()
    else:
        data[new_column] = data[column].ffill()
    return data

