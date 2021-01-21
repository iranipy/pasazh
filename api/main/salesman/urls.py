from main.utils import Helpers
from .views import SalesManView


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('salesman-profile', SalesManView),
]
