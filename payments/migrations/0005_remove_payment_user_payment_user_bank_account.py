# Generated by Django 4.2.7 on 2023-12-03 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("payments", "0004_userwallet_balance"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="payment",
            name="user",
        ),
        migrations.AddField(
            model_name="payment",
            name="user_bank_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="accounts.userbankaccount",
            ),
        ),
    ]
