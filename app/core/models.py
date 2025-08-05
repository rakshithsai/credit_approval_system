from django.db import models

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    monthly_income = models.FloatField()
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, related_name='loans', on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)
