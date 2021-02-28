from main.utils import Helpers
from . import views
gen_url = Helpers.generate_url_item

urlpatterns = [
    gen_url('announcement-email', views.EmailAnnouncement)
]