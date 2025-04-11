from django.shortcuts import render, redirect
from accounting.models import Journal
from .forms import FileUploadForm
from .file_manager import clean_file
from fees.models import Journal

# Create your views here.
def journal_upload(request, pk, df=None):
    template = 'fees/journal_upload.html'
    context = {'df':df}
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            journal = Journal.objects.get(pk=pk)
            data = clean_file(journal.producer.code, request.FILES['file'])
            return redirect('journal_upload', pk=journal.pk, df=data)
    return render(request, template, context=context)

