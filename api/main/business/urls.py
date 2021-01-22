from main.utils import Helpers
from .views import ProductManagement, CategoryManagement, \
ProductAttachmentManagement, OptionManagement, OptionValueManagement


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('product', ProductManagement),
    gen_url('category', CategoryManagement),
    gen_url('product-attachment', ProductAttachmentManagement),
    gen_url('option', OptionManagement),
    gen_url('option-value', OptionValueManagement),
]
