
"""
***************************************************************************************

file_manager.py

This module is designed for:
-parsing files uploaded by the user (ultimately from an external producer)
-converting them for submission to the database (as JournalDetail objects)

File paths should be passed (along with the Producer) into the clean_file function.
The dictionary in the process function maps the Producer to the Producer-specific formatting function.
each Producer function uses a parsing.FileBase class instance with methods for cleaning the raw data.
The Producer function is also wrapped in a decorator that performs format validation and column renaming.

***************************************************************************************
"""

import pandas as pd
import numpy as np


if __name__ == '__main__':
    import file_parsing as parsing
    from file_parsing import ParsePipeline, FileParserConfig
    from producer_dispatcher import ProducerCleanerRegistry
else:
    from . import file_parsing as parsing
    from .producer_dispatcher import ProducerCleanerRegistry
    from .file_parsing import ParsePipeline, FileParserConfig


REQUIRED_COLUMNS = {
    'account_code': str,
    'name': str,
    'product': str,
    'external_adviser': str,
    'bkge_code': str,
    'amount': float,
    'gst': float,
    'lender_amount': float,
    'lender_gst': float,
    'limit': float,
    'balance': float
}



def validate_dataframe(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Function output is not a DataFrame")
    if df.empty:
        raise ValueError("DataFrame is empty")


def rename_columns(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    return df.rename(columns=column_mapping)


def add_missing_columns(df: pd.DataFrame, required_columns: dict) -> pd.DataFrame:
    for col, dtype in required_columns.items():
        if col not in df.columns:
            if dtype == float:
                df[col] = 0.0
            elif dtype == str:
                df[col] = ''
            else:
                df[col] = np.nan
    return df


def clean_and_cast_columns(df: pd.DataFrame, required_columns: dict) -> pd.DataFrame:
    for col, dtype in required_columns.items():
        if col not in df.columns:
            continue
        if dtype == str:
            df[col] = df[col].astype(str).str.replace(r'[$,]+', '', regex=True)
        elif dtype == float:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(r'[$,]+', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df



"""
***************************************************************************************
Producer-specific Processing Functions
These functions are specific to a Producer's data format and are called via the 'process' function.
Each function takes the uploaded file as input and creates an UploadedFileBase instance to store the dataframe.
The Producer functions are decorated with the @formatter decorator, which performs validation and column renaming.
The functions output the UploadedFileBase.data dataframe after making transformations to it.
***************************************************************************************
"""


@ProducerCleanerRegistry.register("SFG")
def sfg_parser(file):
    column_mapping = {'Loan ID': 'account_code', 'Client': 'name',
            'Net Commission (ex GST)': 'amount',
            'Gross Commission (ex GST)': 'lender_amount',
            'Gross Commission (GST)': 'lender_gst',
            'Net Commission GST': 'gst', 'Broker Name': 'external_adviser',
            'Lender': 'product', 'Settlement Amount': 'loan_limit',
            'Loan Balance/Amount': 'balance', 'bkge_code': 'bkge_code'}
    config = FileParserConfig(header_row=0, tab_pattern=r'(Upfront|Clawback|Trail) Details')
    parser = parsing.FileParser(file, config)
    parser.process_xlsx()
    bkg = {'Upfront Details': 'MXI', 'Trail Details': 'MXO', 'Clawback Details': 'MXR'}
    parser.data['bkge_code'] = parser.data['sheet_name'].map(bkg)
    df = (
        ParsePipeline(parser.data)
        .clean_columns()
        .standardise(column_mapping, REQUIRED_COLUMNS)
        .clean_accounts()
        .result()
    )
    return df


@ProducerCleanerRegistry.register("SQ1")
def _sq1(file):
    column_mapping = {'Account Number': 'account_code', 'Borrower': 'name',
            'Payment': 'amount',
            'GST': 'gst',
            'Commission': 'lender_amount',
            'Original Broker': 'external_adviser',
            'lender_gst': 'lender_gst',
            'Lender': 'product', 'Loan Amt': 'loan_limit',
            'Loan Bal': 'balance', 'bkge_code': 'bkge_code'}
    config = FileParserConfig(header_row=5, skip_footer=1)
    parser = parsing.FileParser(file, config)
    parser.process_xlsx()

    parser.data['Borrower'] = parser.data['Borrower'].fillna(parser.data['Loan Bal'])
    parser.data['Account Number'] = parser.data['Account Number'].fillna(parser.data['Loan Bal'])
    parser.data['Loan Bal'] = 0.0
    parser.data['lender_gst'] = parser.data['GST'] / parser.data['Comm Rate']
    bkg = {'Trails': 'MXO', 'Upfront': 'MXI'}
    parser.data['bkge_code'] = bkg[parser.raw_data['Sheet1'].values[4][1]]
    df = (
        ParsePipeline(parser.data)
        .clean_columns()
        .standardise(column_mapping, REQUIRED_COLUMNS)
        .clean_accounts()
        .result()
    )
    return df


@ProducerCleanerRegistry.register("FNS")
def _finsure(file):
    column_mapping = {'Loan Account Number': 'account_code', 'Client': 'name',
            'Amount Paid': 'amount',
            'GST Paid': 'gst',
            'lender_amount': 'lender_amount',
            'lender_gst': 'lender_gst',
            'Lender': 'product', 'loan_limit': 'loan_limit',
            'Loan Balance': 'balance', 'bkge_code': 'bkge_code'}
    config = FileParserConfig(skip_footer=1)
    parser = parsing.FileParser(file, config)
    parser.process_html(data_index_number=0)
    parser.data['Loan Account Number'] = parser.data['Loan Account Number'].fillna('0')
    parser.data.loc[parser.data['Commission Type']=='Adjustments*', 'Commission Type'] = 'ADJUST'
    parser.data['loan_limit'] = parser.data['Loan Balance']
    bkg = {'TRAIL': 'MXO', 'ADJUST': 'FNS', 'UPFRONT': 'MXI'}
    parser.data['bkge_code'] = parser.data['Commission Type'].map(bkg)
    df = (
        ParsePipeline(parser.data)
        .clean_columns()
        .standardise(column_mapping, REQUIRED_COLUMNS)
        .clean_accounts()
        .result()
    )
    return df


