from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import User
from .serializers import UserSerializer


class Login(APIView):

    def post(self, request):
        phone = self.request.data.get('phone')
        if not phone:
            return Response({'message': 'NO_VALID_PHONE'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(mobile=phone)
            return Response({'message': 'OK', 'uid': user.uid}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'NOT_FOUND'}, status=status.HTTP_404_NOT_FOUND)

        except:
            return Response({'message': 'SYSTEM_ERROR'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class UserViewSet(viewsets.ModelViewSet):  # Test
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
