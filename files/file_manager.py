
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
from producer_dispatcher import ProducerCleanerRegistry

if __name__ == '__main__':
    import file_parsing as parsing
else:
    from . import file_parsing as parsing

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


# DECORATOR FUNCTION FOR PRODUCER-SPECIFIC FUNCTIONS
def format_to_standard_schema(column_mapping: dict, required_columns: dict = REQUIRED_COLUMNS):
    def decorator(func):
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            validate_dataframe(df)
            df = rename_columns(df, column_mapping)
            df = add_missing_columns(df, required_columns)
            df = clean_and_cast_columns(df, required_columns)
            return df[list(required_columns.keys())]
        return wrapper
    return decorator


# decorator function
def formatter(new_columns):
    def decorator(func):
        def wrapper(*args, **kwargs):
            df = func(*args, **kwargs)
            # Perform validation checks on the DataFrame
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Function output is not a DataFrame")
            if df.empty:
                raise ValueError("DataFrame is empty")
            df = df.rename(columns=new_columns)[list(new_columns.values())]
            if 'limit' not in df.columns:
                df['limit'] = 0
            if 'balance' not in df.columns:
                df['balance'] = 0
            if 'external_adviser' not in df.columns:
                df['external_adviser'] = np.nan
            if 'bkge_code' not in df.columns:
                df['bkge_code'] = np.nan
            df['account_code'] = df.account_code.astype(str)
            df['name'] = df.name.astype(str)
            df['external_adviser'] = df.external_adviser.astype(str)
            df['bkge_code'] = df.bkge_code.astype(str)
            numerics = ['limit', 'balance', 'amount', 'gst']
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace('[$,]+', '', regex=True)
                    if col in numerics:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            return df[['account_code','name','product','external_adviser','bkge_code',
                       'amount','gst','lender_amount','lender_gst','limit','balance']]
        return wrapper
    return decorator




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
@formatter({'Loan ID': 'account_code', 'Client': 'name',
            'Net Commission (ex GST)': 'amount',
            'Gross Commission (ex GST)': 'lender_amount',
            'Gross Commission (GST)': 'lender_gst',
            'Net Commission GST': 'gst', 'Broker Name': 'external_adviser',
            'Lender': 'product', 'Settlement Amount': 'loan_limit',
            'Loan Balance/Amount': 'balance', 'bkge_code': 'bkge_code'})
def sfg_parser(file):
    b = parsing.FileBase(file)
    b.header_row = 0
    b.process_xlsx(r'(Upfront|Clawback|Trail) Details', engine='openpyxl')
    bkg = {'Upfront Details': 'MXI', 'Trail Details': 'MXO', 'Clawback Details': 'MXR'}
    b.data['bkge_code'] = b.data['tab_name'].map(bkg)
    return b.data





@formatter({'Lender Ref No.': 'account_code', 'Client': 'name',
            'Adviser Share (ex GST)': 'amount',
            'Adviser Share (GST)': 'gst',
            'Supplier Amount (ex GST)': 'lender_amount',
            'Supplier Amount (GST)': 'lender_gst',
            'Product': 'product', 'Original Loan Amount': 'loan_limit',
            'Base Value': 'balance', 'bkge_code': 'bkge_code', 'Adviser':'external_adviser'})
def _sfg(file):
    b = parsing.FileBase(file)
    b.header_row = 11
    b.process_xlsx('Sheet1', engine='xlrd')
    b.data = parsing.drop_cols_by_name(b.data, 'Unnamed')
    b.data = parsing.column_fill(b.data, 'Lender Ref No.', 'Adviser',
           "Client.isnull() and `Lender Ref No.` not in ['New Business','On-Going','Sub Total']")
    b.data = parsing.filter_data(b.data, '~Client.isnull()')
    b.data = parsing.clean_columns(b.data)
    if 'Upfront' in b.raw_data['Sheet1'].iloc[8][0]:
        b.data['bkge_code'] = 'MXI'
    elif 'Trail' in b.raw_data['Sheet1'].iloc[8][0]:
        b.data['bkge_code'] = 'MXO'
    return b.data

@formatter({'Account Number': 'account_code', 'Borrower': 'name',
            'Payment': 'amount',
            'GST': 'gst',
            'Commission': 'lender_amount',
            'Original Broker': 'external_adviser',
            'lender_gst': 'lender_gst',
            'Lender': 'product', 'Loan Amt': 'loan_limit',
            'Loan Bal': 'balance', 'bkge_code': 'bkge_code'})
def _sq1(file):
    b = parsing.FileBase(file)
    b.header_row = 5
    b.skip_footer = 1
    b.process_xlsx('Sheet1', engine='openpyxl')
    b.data['Account Number'] = b.data['Account Number'].fillna('0')
    b.data.loc[b.data['Account Number'] == '0', 'Borrower'] = \
        b.data.loc[b.data['Account Number'] == '0', 'Loan Bal']
    b.data.loc[b.data['Account Number'] == '0', 'Loan Bal'] = np.nan
    for col in ['Loan Amt','Loan Bal','Commission','Comm Rate','Payment','GST','Total Payment']:
        b.data[col] = b.data[col].astype(float)
    b.data['lender_gst'] = b.data['GST'] / b.data['Comm Rate']
    bkg = {'Trails': 'MXO', 'Upfront': 'MXI'}
    b.data['bkge_code'] = bkg[b.raw_data['Sheet1'].values[3][1]]
    return b.data


@formatter({'Loan Account Number': 'account_code', 'Client': 'name',
            'Amount Paid': 'amount',
            'GST Paid': 'gst',
            'lender_amount': 'lender_amount',
            'lender_gst': 'lender_gst',
            'Lender': 'product', 'loan_limit': 'loan_limit',
            'Loan Balance': 'balance', 'bkge_code': 'bkge_code'})
def _finsure(file):
    b = parsing.FileBase(file)
    b.skip_footer = -1
    b.process_html(0)
    b.data.loc[b.data['Loan Account Number'].isna(), 'Loan Account Number'] = 0
    b.data.loc[b.data['Commission Type'] == 'Adjustments*', 'Commission Type'] = 'ADJUST'
    b.data['loan_limit'] = b.data['Loan Balance']
    bkg = {'TRAIL': 'MXO', 'ADJUST': 'FNS', 'UPFRONT': 'MXI'}
    b.data['bkge_code'] = b.data['Commission Type'].map(bkg)
    b.data['lender_amount'] = None
    b.data['lender_gst'] = None
    return b.data


@formatter({'Loan ID': 'account_code', 'Client': 'name',
            'Net Commission (ex GST)': 'amount',
            'Gross Commission (ex GST)': 'lender_amount',
            'Gross Commission (GST)': 'lender_gst',
            'Net Commission GST': 'gst', 'Broker Name': 'external_adviser',
            'Lender': 'product', 'Settlement Amount': 'loan_limit',
            'Loan Balance/Amount': 'balance', 'bkge_code': 'bkge_code'})
def _sfg2(file):
    b = parsing.FileBase(file)
    b.header_row = 0
    b.process_xlsx(r'(Upfront|Clawback|Trail) Details', engine='openpyxl')
    bkg = {'Upfront Details': 'MXI', 'Trail Details': 'MXO', 'Clawback Details': 'MXR'}
    b.data['bkge_code'] = b.data['tab_name'].map(bkg)
    return b.data



# mark for deletion
def clean_file(producer, file):
    """
    clean_file function
    Takes the Producer and file as input and returns the dataframe after processing.
    """
    _dic = {
        'SFGEX': _sfg,
        'SFG': _sfg2,
        'SQ1': _sq1,
        'FNS': _finsure
    }
    if producer not in _dic.keys():
        raise ValueError("Producer not supported")
    output = _dic[producer](file)
    return output


