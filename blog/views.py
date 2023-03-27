from django.shortcuts import render
from .models import Article
from django.http import HttpResponse

# Create your views here.
def list_of_articles(request):
    articles = Article.publishedArticles.all()
    #print(articles)

    #return HttpResponse("this is list of articles webpage...")
    return render(request, 'blog/list.html', {'articles': articles})
    pass