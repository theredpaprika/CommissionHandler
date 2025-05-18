
from django.db.models import QuerySet
from fees.models import Journal, JournalDetail, BkgeClass, Deal, DealSplit, Producer, Agent, Fee
from typing import Optional


class FeeGenerator:

    def __init__(self):
        self.qs: QuerySet[JournalDetail] = None
        self.fees: list[Fee] = []

    def get_journal_details(self, journal:Journal) -> QuerySet[JournalDetail]:
        qs = (
            JournalDetail
            .objects
            .select_related('client_account__deal', 'bkge_class', 'journal__producer')
            .prefetch_related('client_account__deal__splits')
            .filter(journal_id=journal.id)
        )
        self.qs = qs

    def generate_fees(self) -> list[Fee]:
        self.fees = []
        for detail in self.qs:
            journal_detail_splitter = JournalDetailSplitter(detail)
            self.fees += journal_detail_splitter.split()


def create_fee_from_detail(detail:JournalDetail, agent:Agent, split_perc:float) -> Fee:
    return Fee(
        agent=agent,
        detail=detail,
        amount=detail.amount * split_perc / 100,
        gst=detail.gst * split_perc / 100,
    )


class JournalDetailSplitter:
    """
    This class takes a journal detail object, checks the relevant splits to apply and generates a list of Fee objects.
    """

    def __init__(self, detail: JournalDetail):
        self.detail = detail
        self.deal = self.detail.client_account.deal
        self.jd_filter = _JournalDetailFilter(detail)

    def split(self) -> list[Fee]:

        # get list of applicable split rows for journal detail
        filtered_splits = self.jd_filter.get_filtered_splits()
        total_percentage = sum([split.percentage for split in filtered_splits])
        fee_rows = []

        # for each split, generate a Fee row
        for split in filtered_splits:
            agent = split.agent or self.detail.client_account.deal.agent
            split_perc = split.percentage
            new_fee_row = create_fee_from_detail(self.detail, agent, split_perc)
            fee_rows.append(new_fee_row)

        print(self.detail, 'leftovers', 100 - total_percentage)
        # if the sum of split allocation is less than 100%, assign remainder to the deal's primary agent.
        if (remaining_percentage := 100 - total_percentage) > 0:
            print('remaining:',remaining_percentage)
            agent = self.detail.client_account.deal.agent
            new_fee_row = create_fee_from_detail(self.detail, agent, remaining_percentage)
            fee_rows.append(new_fee_row)

        print(self.detail, fee_rows)
        return fee_rows


class _JournalDetailFilter:
    """
    This is a helper class for getting a filtered list of DealSplits for a given JournalDetail
    """

    def __init__(self, detail: JournalDetail):
        self.detail = detail

    def get_filtered_splits(self) -> list[DealSplit]:
        deal = self.detail.client_account.deal
        producer = self.detail.journal.producer
        bkge_class = self.detail.bkge_class
        splits = deal.splits.all()
        filtered_splits = [
            split for split in splits
            if (
                    (split.producer_filter is None or split.producer_filter == producer) and
                    (split.bkge_class_filter is None or split.bkge_class_filter == bkge_class)
            )
        ]
        return filtered_splits




