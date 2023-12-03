from .models import UserWallet
from rest_framework import serializers



class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = '__all__'


