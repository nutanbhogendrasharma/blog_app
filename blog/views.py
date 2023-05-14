from django.shortcuts import render, get_object_or_404
from .models import Article, Comment
from django.http import HttpResponse
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm, SearchForm
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count

# Create your views here.
def list_of_articles(request, tag_slug = None):
    articles = Article.publishedArticles.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags__in=[tag])

    paginator = Paginator(articles, 3)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        articles = paginator.page(1)

    return render(request, 'blog/list.html', {'articles': articles, 'tag': tag})
    pass

def article_details(request, year, month, day, article):
    try:
        article = get_object_or_404(Article, status=Article.Status.PUBLISHED, 
                    slug=article,
                    publish__year=year,
                    publish__month=month,
                    publish__day=day
                )

        # List of active comments for this article
        comments = article.comments.filter(active=True)

        # Form for users to write comment
        form = CommentForm()

        # Retrieving list of similar articles
        article_tags_ids = article.tags.values_list('id', flat=True)
        similar_published_articles = Article.publishedArticles.filter(tags__in=article_tags_ids)\
                                        .exclude(id=article.id)
        similar_articles = similar_published_articles.annotate(same_tags_in_article=Count('tags'))\
                                        .order_by('-same_tags_in_article','-publish')[:3]
        
    except Article.DoesNotExist:
        raise Http404("No article found.")
    
    return render(request, 'blog/detail.html', {
                'article': article,
                'comments': comments,
                'form': form,
                'similar_articles': similar_articles
            }
        )
    pass


@require_POST
def comment_for_article(request, article_id):

    # get the article by article_id
    article = get_object_or_404(Article, id = article_id, status=Article.Status.PUBLISHED)
    comment = None
    
    # A comment form
    form = CommentForm(data=request.POST)

    if form.is_valid():
        # Create a Comment object before saving it to the database
        comment = form.save(commit=False)

        # Assign the article to the comment
        comment.article = article

        # Save the comment to the database
        comment.save()
        pass

    return render(request, 'blog/comment.html', {'article': article, 'form': form, 'comment': comment})

    pass

def article_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Article.objects.raw("SELECT * FROM blog_article WHERE MATCH (title, body) AGAINST (%s)", [query])
            pass
        pass
    
    return render(request,
            'blog/search.html',
            {'form': form, 'query': query,'results': results}
        )

    pass