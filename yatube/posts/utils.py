from django.core.paginator import Paginator
from yatube.settings import PUB_COUNT


def get_page(request, post_list):
    paginator = Paginator(post_list, PUB_COUNT)
    page_numbers = request.GET.get('page')
    return paginator.get_page(page_numbers)
