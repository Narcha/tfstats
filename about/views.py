from django.shortcuts import render

# Create your views here.
def about(request):
    return render(request, "about.html", {"page_name": "About"})