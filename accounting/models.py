from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils.text import slugify
from django.utils.timezone import now
from django.db import models
from datetime import datetime, timedelta
import calendar

class CommissionPeriod(models.Model):
    end_date = models.DateField(unique=True)  # Last day of the month
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_existing_period(cls):
        return cls.objects.filter(processed=False).first()

    @classmethod
    def get_next_period(cls, previous_date):
        new_month = previous_date + relativedelta(day=+1)
        last_day = calendar.monthrange(new_month.year, new_month.month)[1]
        end_new_month = new_month.replace(day=last_day)
        return cls.objects.get_or_create(end_date=end_new_month)

    @classmethod
    def get_create_current_period(cls):
        """Returns the existing commission period for this month or creates a new one."""
        today = now().date()
        last_day = cls.get_last_day_of_month(today)
        period, created = cls.objects.get_or_create(end_date=last_day)
        return period

    @classmethod
    def close_and_create_new_period(cls):
        """Closes the current period and creates a new one for the next month."""
        current_period = cls.get_existing_period()
        if not current_period.processed:
            current_period.processed = True
            current_period.save()

        # Create the next month's period
        next_month_date = current_period.end_date + timedelta(days=1)  # First day of next month
        next_last_day = cls.get_last_day_of_month(next_month_date)
        new_period, created = cls.objects.get_or_create(end_date=next_last_day)
        return new_period

    @staticmethod
    def get_last_day_of_month(date):
        """Returns the last day of the month for a given date."""
        last_day = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=last_day)

    def get_period_fees(self, agent=None, producer=None, bkge_class=None):
        return Entry.objects.filter(journal_detail__journal__commission_period=self).all()

    def __str__(self):
        return f"{self.end_date.strftime('%Y-%m-%d')}"


class Account(models.Model):
    account_code = models.CharField(max_length=8)
    account_subtype = models.ForeignKey('AccountSubtype', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=1)

    def balance(self):
        return self.entries.all().aggregate(balance=Sum('amount')).get('balance') or 0

    def __str__(self):
        return f"{self.account_code} - {self.name}"


def slugify_instance_name(instance, save=False):
    slug = slugify(instance.name)
    qs = Account.objects.filter(slug=slug).exclude(id=instance.id)
    if qs.exists():
        slug = f"{slug}-{qs.count()+1}"
    instance.slug = slug
    if save:
        instance.save()


class Journal(models.Model):
    date = models.DateField(auto_now_add=True)
    period_end_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = None

    def __str__(self):
        return f"Journal Entry: {self.date} - {self.reference} - {self.description} "


class Entry(models.Model):
    date = models.DateField(auto_now_add=True)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='entries')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1)
    notes = models.CharField(max_length=100, blank=True)

    def account_code(self):
        return self.account.account_code

    def __str__(self):
        if self.amount < 0:
            return f"CR {abs(self.amount)} to {self.account.name}"
        else:
            return f"DR {abs(self.amount)} to {self.account.name}"


class AccountType(models.Model):
    account_type_code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return  f"{self.account_type_code}"


class AccountSubtype(models.Model):
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    account_subtype_code = models.CharField(max_length=8)
    is_cumulative = models.BooleanField(default=True)
    is_contra = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return  f"{self.account_subtype_code} ({self.account_type.account_type_code}) - {self.name}"

