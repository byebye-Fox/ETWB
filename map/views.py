from django.shortcuts import render

from django.http import JsonResponse,HttpResponseRedirect

key = 1 


# Create your views here.
def map(request):
    return render(request, 'map/map.html')