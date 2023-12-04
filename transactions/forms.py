from .constants import WITHDRAWAL  # Assuming you have this constant defined
import datetime
from django import forms
from payments.models import UserWallet
from django.conf import settings
from .models import Transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class TransactionDateRangeForm(forms.Form):
    daterange = forms.CharField(required=False)

    def clean_daterange(self):
        daterange = self.cleaned_data.get("daterange")
        print(daterange)

        try:
            daterange = daterange.split(' - ')
            print(daterange)
            if len(daterange) == 2:
                for date in daterange:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                return daterange
            else:
                raise forms.ValidationError("Please select a date range.")
        except (ValueError, AttributeError):
            raise forms.ValidationError("Invalid date range")


class WithdrawForm(TransactionForm):
    def clean_amount(self):

        account = self.account
        user_wallet = UserWallet.objects.get(user=account.user)
        min_withdraw_amount = getattr(settings, 'MINIMUM_WITHDRAWAL_AMOUNT', 0)
        max_withdraw_amount = account.account_type.maximum_withdrawal_amount

        balance = user_wallet.balance
        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                _('You can withdraw at least %(amount)s $') % {
                    'amount': min_withdraw_amount}
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                _('You can withdraw at most %(amount)s $') % {
                    'amount': max_withdraw_amount}
            )

        if amount > balance:
            raise forms.ValidationError(
                _('You have %(balance)s $ in your account. You cannot withdraw more than your account balance') % {
                    'balance': balance}
            )

        return amount

    def clean_withdrawal(self):
        amount = self.cleaned_data.get('amount')
        # Implement a method to get or calculate the recipient code
        recipient_code = self.get_recipient_code()

        max_withdrawal_limit = self.get_paystack_max_withdrawal_limit(
            recipient_code)

        if amount > max_withdrawal_limit:
            raise forms.ValidationError(
                _('You can withdraw at most %(amount)s $ using Paystack') % {
                    'amount': max_withdrawal_limit}
            )

        return amount

    def get_recipient_code(self):
        # Implement a method to get or calculate the recipient code
        pass

    def get_paystack_max_withdrawal_limit(self, recipient_code):
        # Implement a method to get Paystack withdrawal limits
        pass
