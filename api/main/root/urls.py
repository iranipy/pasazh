from main.utils import Helpers
from .views import EmailAnnouncement


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('announcement-email', EmailAnnouncement),
]
