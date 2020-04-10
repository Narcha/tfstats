from django.shortcuts import redirect
from django.core.handlers.wsgi import WSGIRequest

# Create your views here.
def search(request: WSGIRequest):
    query = request.GET["query"]
    return redirect("/profiles/" + query)