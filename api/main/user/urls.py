from main.utils import Helpers
from .views import UpdateUserProfile, Follow, Block


gen_url = Helpers.generate_url_item


urlpatterns = [
    gen_url('update-profile', UpdateUserProfile),
    gen_url('follow', Follow),
    gen_url('block', Block),
]
