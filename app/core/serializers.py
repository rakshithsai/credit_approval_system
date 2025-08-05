from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class RegisterSerializer(serializers.Serializer):
    first_name=serializers.CharField()
    last_name=serializers.CharField()
    age=serializers.IntegerField()
    monthly_income=serializers.FloatField()
    phone_number=serializers.CharField()

class CheckEligibilitySerializer(serializers.Serializer):
    customer_id=serializers.IntegerField()
    loan_amount=serializers.FloatField()
    interest_rate=serializers.FloatField()
    tenure=serializers.IntegerField()

class CreateLoanSerializer(CheckEligibilitySerializer):
    pass

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'
