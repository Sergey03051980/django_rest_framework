from rest_framework.pagination import PageNumberPagination

class MaterialsPaginator(PageNumberPagination):
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов
    max_page_size = 50  # Максимальное количество элементов на странице
