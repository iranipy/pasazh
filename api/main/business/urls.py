from main.utils import Helpers
from .views import ProductManagement, CategoryManagement


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('product', ProductManagement),
    gen_url('category', CategoryManagement),
]
