from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


##
## Start of local vars.
##
localCopy = "<hr width=80%>(&copy;)2018  Henrique Moreira"
##
## end of local vars.
##


posts = [
    {
     'author': 'Jose Saramago',
     'title': 'Blog Post 1',
     'content': 'First post content',
     'date_posted': 'August 27, 2018'
    },
    {
     'author': 'Eca Queiroz',
     'title': 'Blog Post 2',
     'content': 'Second post content',
     'date_posted': 'August 28, 2018'
    }
]


def home_DEFAULT (request):
    return HttpResponse('<h1>Blog home</h1>'+localCopy)


def home (request):
    context = {
        'posts': posts,
        'title': 'sweet home!'
    }
    return render(request, 'blog/home.html', context)


def about_DEFAULT (request):
    coreText = """
	This is the basic 'About' page of my blog, under /blog/about/<br>
"""
    return HttpResponse('<h1>Blog about</h1>'+coreText+localCopy)


def about (request):
    return render(request, 'blog/about.html')

