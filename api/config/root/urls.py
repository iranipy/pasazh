from config.utils import Helpers

from .views import ConfigRetrieve
generate_url = Helpers.generate_url_item

urlpatterns = [
    generate_url('config-retrieve', ConfigRetrieve)
]