from django.shortcuts import render, get_object_or_404
from .models import Article

def news_list(request):
    articles = Article.objects.filter(is_published=True).order_by('-publish_date')
    return render(request, 'news/news_list.html', {'articles': articles})

def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, 'news/news_detail.html', {'article': article})
