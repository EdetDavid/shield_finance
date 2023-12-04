from django.shortcuts import render, redirect
from .models import Payment, UserWallet
from django.conf import settings
from accounts.models import UserBankAccount
from django.shortcuts import get_object_or_404

def initiate_payment(request):
    user_bank_accounts = UserBankAccount.objects.all()

    if request.method == "POST":
        account_number = request.POST['account_number']
        amount = request.POST['amount']
        email = request.POST['email']

        # Convert account_number to integer if not empty
        user_bank_account = None
        if account_number.strip():  # Check if not empty or blank
            account_number = int(account_number)
            user_bank_account = get_object_or_404(
                UserBankAccount, account_no=account_number)

        # Create and save the Payment object with the associated user
        payment_user = user_bank_account.user if user_bank_account else request.user
        payment = Payment.objects.create(
            amount=amount, email=email, user=payment_user)
        payment.save()

        pk = settings.PAYSTACK_PUBLIC_KEY

        context = {
            'payment': payment,
            'field_values': request.POST,
            'paystack_pub_key': pk,
            'amount_value': payment.amount_value(),
        }
        return render(request, 'transactions/make_payment.html', context)

    context = {'user_bank_accounts': user_bank_accounts}
    return render(request, 'transactions/payment.html', context)


def verify_payment(request, ref):
    payment = Payment.objects.get(ref=ref)
    verified = payment.verify_payment()

    if verified:
        user_wallet = UserWallet.objects.get(user=payment.user)
        user_wallet.balance += payment.amount
        user_wallet.save()
        print(request.user.email, " funded wallet successfully")
        return render(request, "transactions/success.html")
    return render(request, "transactions/success.html")
