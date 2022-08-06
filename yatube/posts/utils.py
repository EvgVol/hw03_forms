from django.conf import settings
from django.core.paginator import Paginator


def paginator_posts(request, queryset):
    """Описывает работу пагинатора постов."""
    paginator = Paginator(queryset, settings.CONST_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj