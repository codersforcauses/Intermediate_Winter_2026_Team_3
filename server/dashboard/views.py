
# Create your views here.
from django.shortcuts import render

def login_test(request):
    return render(request, 'dashboard/login_test.html')