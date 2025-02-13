from django.db import models
from django.db.models import Sum
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save


from django.db.models.signals import post_save
from django.dispatch import receiver


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

