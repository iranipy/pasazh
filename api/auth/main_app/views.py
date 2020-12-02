from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from .models import User
from .serializers import UserSerializer
from .utils import CustomResponse

custom_response = CustomResponse()


class Login(APIView):
    def post(self, request):
        phone = self.request.data.get('phone')
        if not phone:
            return custom_response.bad_request()
        try:
            user = User.objects.get(mobile=phone)
            response = custom_response.success(uid=user.uid)
            custom_response.reset_message()
            return response
        except User.DoesNotExist:
            return custom_response.not_found()

        # except:
        #     return custom_response.system_error(503)


class Verify(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DeleteAccount(APIView):
    def put(self, request):
        phone = self.request.data.get('phone')
        if not phone:
            return custom_response.bad_request()
        try:
            user = User.objects.get(mobile=phone)
            user.is_deleted = True
            user.is_active = False
            user.save()
            return custom_response.success()
        except User.DoesNotExist:
            return custom_response.not_found()
        # except:
        #     return custom_response.system_error()
