from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "global_stats.html", {"page_name": "Global Stats"})