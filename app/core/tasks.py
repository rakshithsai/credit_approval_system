from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from django.utils import timezone
@shared_task
def ingest():
    df = pd.read_excel('customer_data.xlsx')
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            id=row.customer_id,
            defaults={
                'first_name': row.first_name,
                'last_name': row.last_name,
                'phone_number': str(row.phone_number),
                'monthly_income': row.monthly_salary,
                'approved_limit': row.approved_limit,
                'current_debt': row.current_debt,
            }
        )
    df2 = pd.read_excel('loan_data.xlsx')
    for _, row in df2.iterrows():
        Loan.objects.update_or_create(
            loan_amount=row['loan amount'], tenure=row.tenure,
            interest_rate=row['interest rate'], customer_id=row['customer id'],
            defaults={
                'monthly_installment': row['monthly repayment'],
                'emis_paid_on_time': row['EMIs paid on time'],
                'start_date': row['start date'],
                'end_date': row['end date'],
                'active': True,
            }
        )
