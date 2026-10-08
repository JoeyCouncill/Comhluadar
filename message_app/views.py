from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

def inbox(request):
	return render(request, "inbox.html")