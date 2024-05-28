from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class InmueblePagination(PageNumberPagination):
    page_size = 2
    page_query_param = 'p'
    max_page_size = 10
    last_page_strings = 'end'
    
class InmuebleLOPagination(LimitOffsetPagination):
    default_limit = 1