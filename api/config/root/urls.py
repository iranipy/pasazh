from config.utils import Helpers
from .views import Config


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('config', Config),
]
