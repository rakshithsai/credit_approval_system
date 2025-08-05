from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import *
import math
from datetime import date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

class RegisterView(APIView):
    def post(self, req):
        s=RegisterSerializer(data=req.data); s.is_valid(raise_exception=True)
        cd=s.validated_data
        approved=round(36*cd['monthly_income'] / 1e5)*1e5
        cust=Customer.objects.create(
            first_name=cd['first_name'], last_name=cd['last_name'],
            age=cd['age'], monthly_income=cd['monthly_income'],
            phone_number=cd['phone_number'], approved_limit=approved
        )
        return Response({
            'customer_id': cust.id,
            'name': f"{cust.first_name} {cust.last_name}",
            'age': cust.age,
            'monthly_income': cust.monthly_income,
            'approved_limit': cust.approved_limit,
            'phone_number': cust.phone_number
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def api_root(request):
    return Response({"message": "API is working"})


def api_view(request):
    return JsonResponse({"message": "Hello from the function-based view!"})

def compute_credit_score(customer: Customer):
    loans = customer.loans.all()
    on_time = sum(l.emis_paid_on_time for l in loans)
    total_loans = loans.count()
    this_year = sum(1 for l in loans if l.start_date.year == date.today().year)
    vol = sum(l.loan_amount for l in loans)
    if customer.current_debt>customer.approved_limit:
        return 0
    score = (on_time * 1.0) + max(0, 10 - total_loans)*2 + max(0, 5-this_year)*1
    score -= vol/1e5
    return max(0, min(100, score))

def monthly_installment(amount, rate, tenure):
    r = rate/12/100
    n=tenure
    return r * amount / (1-(1+r)**(-n))

class CheckEligibilityView(APIView):
    def post(self, req):
        s=CheckEligibilitySerializer(data=req.data); s.is_valid(raise_exception=True)
        cd=s.validated_data
        try:
            cust=Customer.objects.get(id=cd['customer_id'])
        except:
            return Response({'error':'customer not found'}, status=status.HTTP_404_NOT_FOUND)
        score=compute_credit_score(cust)
        approved=False; corr=cd['interest_rate']
        if cust.current_debt > 0.5*cust.monthly_income:
            approved=False
        else:
            if score>50: approved = True
            elif 30<score<=50:
                if cd['interest_rate']>12: approved=True
                else: corr=12
            elif 10<score<=30:
                if cd['interest_rate']>16: approved=True
                else: corr=16
        mni = monthly_installment(cd['loan_amount'], corr, cd['tenure'])
        return Response({
            'customer_id':cust.id,
            'approval': approved,
            'interest_rate': cd['interest_rate'],
            'corrected_interest_rate': corr,
            'tenure': cd['tenure'],
            'monthly_installment': mni
        })

class CreateLoanView(APIView):
    def post(self, req):
        check = CheckEligibilityView().post(req)
        if not check.data['approval']:
            return Response({
                'loan_id': None,
                'customer_id': req.data.get('customer_id'),
                'loan_approved': False,
                'message': 'Loan not approved',
                'monthly_installment': None
            })
        cd=req.data; cust=Customer.objects.get(id=cd['customer_id'])
        corr = check.data['corrected_interest_rate']
        mni = check.data['monthly_installment']
        loan=Loan.objects.create(customer=cust, loan_amount=cd['loan_amount'],
                tenure=cd['tenure'], interest_rate=corr,
                monthly_installment=mni, start_date=date.today(),
                end_date=date.today(), emis_paid_on_time=0)
        cust.current_debt += cd['loan_amount']
        cust.save()
        return Response({
            'loan_id': loan.id,
            'customer_id': cust.id,
            'loan_approved': True,
            'message': 'Loan approved',
            'monthly_installment': mni
        })

class ViewLoanView(APIView):
    def get(self, req, loan_id):
        try:loan=Loan.objects.get(id=loan_id)
        except: return Response(status=status.HTTP_404_NOT_FOUND)
        c=loan.customer
        return Response({
            'loan_id': loan.id,
            'customer': {
                'id':c.id,'first_name':c.first_name,'last_name':c.last_name,'phone_number':c.phone_number,'age':c.age
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_installment,
            'tenure': loan.tenure
        })

class ViewLoansByCustomer(APIView):
    def get(self, req, customer_id):
        loans=Loan.objects.filter(customer_id=customer_id, active=True)
        out=[]
        for l in loans:
            repayments_left = l.tenure  # simplify
            out.append({
                'loan_id':l.id,
                'loan_amount': l.loan_amount,
                'interest_rate': l.interest_rate,
                'monthly_installment': l.monthly_installment,
                'repayments_left': repayments_left
            })
        return Response(out)
