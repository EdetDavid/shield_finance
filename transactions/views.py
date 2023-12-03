from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from transactions.constants import WITHDRAWAL
from transactions.forms import (
    TransactionDateRangeForm,
    WithdrawForm,
)
from transactions.models import Transaction
import paystack
from django.conf import settings
from django.shortcuts import render, redirect
from payments.models import UserWallet, Payment
from django.conf import settings
from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404


User = get_user_model()


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_wallet = UserWallet.objects.all().filter(user=self.request.user)
        # Retrieve the UserWallet instance for the logged-in user
        balance = UserWallet.objects.filter(
            user=self.request.user).values("balance")

        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None),
            'balance': balance,
            'user_wallet': user_wallet
        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''

    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,

        })
        return kwargs

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,

        })

        return context


# class WithdrawMoneyView(TransactionCreateMixin):
#     form_class = WithdrawForm
#     title = 'Withdraw Money from Your Account'
#     user_wallet = UserWallet.objects.all()

#     def get_initial(self):
#         initial = {'transaction_type': WITHDRAWAL}
#         return initial

#     def form_valid(self, form):
#         payment = Payment.objects.get(ref=ref)
#         amount = form.cleaned_data.get('amount')
#         recipient_code = form.get_recipient_code()
#         balance = UserWallet.objects.filter(
#             user=self.request.user).values("balance")
#         user_wallet = UserWallet.objects.get(user=request.user)
#         user_wallet.balance += payment.amount
#         user_wallet.save()

#         # Perform Paystack withdrawal here
#         paystack_secret_key = settings.PAYSTACK_SECRET_KEY
#         paystack.api_key = paystack_secret_key

#         return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    template_name = 'transactions/transaction_form.html'  # Replace with your actual template

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        ref = form.cleaned_data.get('ref')
        amount = form.cleaned_data.get('amount')
        recipient_code = form.get_recipient_code()

        user_wallet = get_object_or_404(UserWallet, user=self.request.user)
        user_wallet.balance -= amount
        user_wallet.save()

        # Perform Paystack withdrawal here
        paystack_secret_key = settings.PAYSTACK_SECRET_KEY
        paystack.api_key = paystack_secret_key

        # Now you can use self.request to access the request object
        # For example, self.request.user, self.request.method, etc.

        return super().form_valid(form)
