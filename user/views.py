from django.http import JsonResponse
from rest_framework import generics,status
from.serializers import SignUpSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

User = get_user_model()

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

        
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data,context={'user': user})
        serializer.is_valid(raise_exception=True)
     
        tokens = serializer.validated_data['tokens']
        
        print(user,tokens)
        if not (tokens and user):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
   
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(tokens),
            'refresh': str(refresh),     
        }) 



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            token = auth_header.split(" ")[1] 
        else:
            return Response({"error": "No token found"}, status=401)

        try:
            payload = jwt.decode(token,  settings.SECRET_KEY, algorithms=['HS256'])
            
            user_id = payload.get('user_id')  
            user = User.objects.get(id=user_id)
         
      
            return Response({
                'username': user.username,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'mobile_number': user.mobile_number,
            })
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expired"}, status=401)
        except jwt.DecodeError:
            return Response({"error": "Invalid token"}, status=401)