from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
import tempfile
from . import utils
import re
import os
from django.utils.encoding import smart_str
from datetime import datetime
import time
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from .models import *
import requests
from urllib.parse import urlparse
from django.urls import reverse
from . import api


def index(request):
	context = dict()
	return render(request, "index.html", context)


@require_POST
def translate_text(request):
	text = request.POST["text"].strip()
	response = api.translate_string(text, "spa", "arg", "apertium", "txt")
	if response:
		translation = response["translated_text"]
		words = response["words"]
		Statistic.objects.create(words=words, type="text", document_type="txt")
	else:
		print(response.content)
	
	return JsonResponse({'translation':translation})

@require_POST
def translate_document(request):
	print("New document request")
	document = request.FILES["document"]
	filename, file_extension = os.path.splitext(document.name)
	file_extension = file_extension[1:].lower()
	if not file_extension in ["docx", "xlsx", "pptx", "odt", "txt", "html"]:
		raise Exception("Unsupported format")

	timestamp = str(datetime.timestamp(datetime.now()))

	in_filename = f"{timestamp}.{file_extension}"

	fs = FileSystemStorage()
	fin_name = fs.save(in_filename, document)
	fin_url = fs.url(fin_name)
	fin_path = fs.path(fin_name)
	
	fin_basename, fin_extension = os.path.splitext(fin_name)

	fout_name = f"{fin_basename}_trad.{file_extension}"
	fout_path = os.path.join(fs.location, fout_name)


	fin = open(fin_path, "wb")
	for chunk in document.chunks():
		fin.write(chunk)
	fin.close()

	print("Sending document to API")        
	translated_file = api.translate_file(fin_path, "spa", "arg", "apertium", file_extension)
	print("Response from API")
	print(translated_file)        
	if translated_file:
		with open(fout_path, "wb") as fout:
			response = requests.get(settings.API_URL + translated_file["translated_file"])
			if response.status_code == 200:
				fout.write(response.content)
			else:
				print(response.content)
				raise Exception("Error downloading file from API")                                
		words = translated_file["words"]
		Statistic.objects.create(words=words, type="file", document_type=file_extension)

		os.remove(fin_path)
		#os.remove(fout_path)
		                
		return JsonResponse({'translated_file':fs.url(fout_name)})

	os.remove(fin_path)
	raise Exception("Error while translating file")

@require_GET
def translate_url(request):
	url = request.GET["url"]


	resp = requests.get(url)
	html = resp.text

	fin = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".html")
	fout = tempfile.NamedTemporaryFile(mode="wb", suffix=".html")
	ffin = tempfile.NamedTemporaryFile(mode="r", encoding="utf-8", suffix=".html")
	fin.write(html)
	fin.seek(0)
	in_path = fin.name
	out_path = fout.name
	
	print("Sending document to API")
	translated_file = api.translate_file(in_path, "spa", "arg", "apertium", "html")
	if translated_file:
		response = requests.get(settings.API_URL + translated_file["translated_file"])
		if response.status_code == 200:
			translation = response.content.decode()
		words = translated_file["words"]
		print("ONOD")
		#os.rename(fout.name, ffin.name)
		#translation = ffin.read()

	# from urlparse import urlparse  # Python 2
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


	# Complete relative urls
	translation = re.sub(r"href=\"/", rf'href="{domain}/', translation)
	translation = re.sub(r"src=\"/", rf'src="{domain}/', translation)

	# Precede links with traduze url
	translation = re.sub("<a .* ?href=\"([^\"]+)\"", r'<a href="' + reverse("translate_url") + r'?url=\1"', translation)
	translation = re.sub('target="_blank"', "", translation)


	Statistic.objects.create(words=words, type="url", document_type="html")

	print("Responding")
	response = HttpResponse(translation)
	response['X-Frame-Options'] = 'sameorigin'
	#response = render(request, "reader.html", context={'translation':translation})
	#response['X-Frame-Options'] = 'sameorigin'
	return response


def reader(request):
	#url = request.GET["url"]
	return render(request, "reader.html", context={})


def contact(request):
	return render(request, "info/contact.html", context={})

def help(request):
	return render(request, "info/help.html", context={})

def legal_notice(request):
	return render(request, "info/legal_notice.html", context={})

def privacy_policy(request):
	return render(request, "info/privacy_policy.html", context={})
