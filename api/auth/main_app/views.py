from .models import User
from .utils import CustomResponse, MetaApiViewClass
from rest_framework.generics import RetrieveAPIView
# from .serializers import UserSerializer


class Login(MetaApiViewClass):

    @MetaApiViewClass.generic_decor
    def post(self, request):
        mobile = self.request.data.get('mobile')
        if not mobile:
            return CustomResponse.bad_request(message=['MOBILE_PARAMETER_IS_REQUIRED'])
        try:
            user = User.objects.get(mobile=mobile)
            return CustomResponse.success(data={'uid': user.uid})
        except User.DoesNotExist:
            return CustomResponse.not_found()


# uncomment when finished
class Verify(RetrieveAPIView):
    pass
    #     queryset = User.objects.all()
    #     serializer_class = UserSerializer


# should delete account based on userId extracted from token
class DeleteAccount(MetaApiViewClass):
    pass
    #     def put(self, request):
    #         phone = self.request.data.get('phone')
    #         if not phone:
    #             return custom_response.bad_request()
    #         try:
    #             user = User.objects.get(mobile=phone)
    #             user.is_deleted = True
    #             user.is_active = False
    #             user.save()
    #             return custom_response.success()
    #         except User.DoesNotExist:
    #             return custom_response.not_found()
