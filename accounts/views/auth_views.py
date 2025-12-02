from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import UserSerializer


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    # Skip DRF authentication on this endpoint so invalid tokens in headers
    # don't produce a 401 before the view code runs.
    authentication_classes = []
    
    def create(self, request, *args, **kwargs):
        
        response = super().create(request, *args, **kwargs)
        # Run serializer validation
        user = User.objects.get(username=response.data['username'])
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User created successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': response.data
        }, status=status.HTTP_201_CREATED)
        



class LoginView(APIView):
   
    permission_classes = [permissions.AllowAny]
    # Don't run authentication on login endpoint (frontend may not yet have valid token)
    authentication_classes = []
    
    def post(self, request):
 
        # Support login by username or email
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # If email provided but no username, try to resolve the username
        if not username and email:
            try:
                user_by_email = User.objects.filter(email__iexact=email).first()
                if user_by_email:
                    username = user_by_email.username
                    print(f"Resolved email {email} to username {username}")
                else:
                    print(f"No user found with email: {email}")
            except Exception as e:
                print("Error while resolving email to username:", e)

        print(f"Attempting authenticate for username={username} password_provided={bool(password)})")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)