from django.urls import path

from .views import *


app_name = 'transactions'


urlpatterns = [
    path("report/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),

]
