from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100
