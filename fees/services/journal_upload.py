from ..models import ProducerClient, JournalDetail, BkgeClass, Producer
import pandas as pd

def add_missing_accounts(df, journal, user):
    accounts = df.account_code.unique().tolist()
    accounts_not_in_db = check_unallocated_accounts(accounts, journal.producer)
    missing_df = df[df.account_code.isin(accounts_not_in_db)]
    missing_accounts = missing_df[['account_code', 'name']].drop_duplicates()

    for account_code, name in missing_accounts.itertuples(index=False):
        ProducerClient.objects.create(
            producer=journal.producer,
            client_code=account_code,
            name=name,
            deal=None,
            created_by=user,
            updated_by=user
        )

def create_journal_details(df, journal_id, producer_id):
    bkge_map = {x.code: x.id for x in BkgeClass.objects.all()}
    account_map = {
        x.client_code: x.id
        for x in ProducerClient.objects.filter(producer_id=producer_id)
    }

    df['bkge_class_id'] = df['bkge_code'].map(bkge_map)
    df['journal_id'] = journal_id
    df['client_account_code_id'] = df.account_code.map(account_map)
    df.fillna({
        'amount': 0, 'gst': 0, 'lender_amount': 0,
        'lender_gst': 0, 'balance': 0, 'limit': 0
    }, inplace=True)

    jd_objs = [
        JournalDetail(
            journal_id=row['journal_id'],
            bkge_class_id=row['bkge_class_id'],
            client_account_code_id=row['client_account_code_id'],
            product=row['product'],
            external_adviser=row['external_adviser'],
            amount=row['amount'],
            gst=row['gst'],
            details=row['name'],
            lender_amount=row['lender_amount'],
            lender_gst=row['lender_gst'],
            balance=row['balance'],
            limit=row['limit'],
        )
        for _, row in df.iterrows()
        if not any(pd.isna(row[f]) for f in ['journal_id', 'bkge_class_id', 'client_account_code_id'])
    ]

    JournalDetail.objects.bulk_create(jd_objs, batch_size=500)


def check_unallocated_accounts(account_list: list, producer: Producer):
    """
    Checks a list of producer client accounts (account_list) against ProducerClient.client_code
    and returns a subset of producer client accounts that are not in the database.

    example:
    If ProducerClient contains accounts: ['100', '101', '102'] under producer "ABC":
    check_unallocated_accounts(['100', '101', '102', '103'], "ABC") returns ['103']
    """
    # get list from db filtered by account list provided
    _existing_clients = (
        ProducerClient
        .objects
        .filter(
            producer=producer,
            client_code__in=account_list
        )
        .all()
        .values_list('client_code', flat=True)
    )
    accounts = [str(i).replace('.0','') for i in account_list]
    existing = [str(i) for i in _existing_clients]
    return list(set(accounts) - set(existing))

