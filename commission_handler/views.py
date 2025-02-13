
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from fees.models import Journal

# Create your views here

def home_view(request):
    return render(request, 'home.html')

def test_view(request):
    template = 'test.html'
    objs = Journal.objects.all()
    context = {'objs': objs}
    return render(request, template, context=context)