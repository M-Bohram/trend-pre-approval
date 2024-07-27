'''
API Views Documentation

This module defines custom API views for user authentication, registration, and CRUD operations in our project.

Attributes:
    MyTokenObtainPairSerializer: A custom token obtain pair view for token authentication.
    UserRegisterView: A view for user registration.
    DisplayList: A view for displaying a list of users and creating new users.
    DisplayDetail: A view for displaying, updating, and deleting individual user instances.

Usage:
    To use these views in our Django REST Framework views, import them into the relevant modules of our project.
    These views handle various aspects of user authentication, registration, and management, providing endpoints for user-related operations.

    Example usage in views:

    # User authentication
    urlpatterns = [
        'login/', MyTokenObtainPairSerializer.as_view(), name='login'),
    ]

    # User registration
    urlpatterns = [
        path('register/', UserRegisterView.as_view(), name='register'),
    ]

    # CRUD operations
    urlpatterns = [
    path('users/', DisplayList.as_view(), name='users'),
    path('users/<int:pk>/', DisplayDetail.as_view(), name='users'),
    ]

'''

from .models import CustomUser, Block
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsBlockerSelf
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import BlockListSerializer, MyTokenObtainPairSerializer, CustomUserRegistrationSerializer,  ResetPasswordEmailSerializer, CheckCodeSerializer, ConfirmPasswordSerializer, BlockSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError




# login
class MyTokenObtainPairSerializer(TokenObtainPairView):
    '''
    Custom Token Obtain Pair View

    This view is used for token authentication in our project. It extends the default TokenObtainPairView provided by Django REST Framework SimpleJWT.

    Method: POST
    Body :
    {
    "username":"rania",
    "password":"123test"
    }

    '''
    serializer_class = MyTokenObtainPairSerializer


class UserRegisterView(CreateAPIView):
    '''
    User Registration View

    This view handles user registration in our project.
    Method: POST
    Body :
    {
    "username":"rania",
    "password":"123test"
    }
    '''
    serializer_class = CustomUserRegistrationSerializer


    def post(self, request, *args, **kwargs):
        '''
        POST Method

        Overrides the post method to handle user registration.
        '''
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {
                'response': 'Successfully registered new user.',
                'email': serializer.data['email'],
                'username': serializer.data['username'],
                'avatar': serializer.data['avatar'],
            }
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# CRUD
class DisplayList(generics.ListCreateAPIView):
    '''
    User List and Create View

    This view displays a list of users and handles user creation in our project.
    '''
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer


class DisplayDetail(generics.RetrieveUpdateDestroyAPIView):

    '''
    User Detail View

    This view displays, updates, and deletes individual user instances in our project.
    '''
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRegistrationSerializer


# forgot password views
class PasswordResetRequestView(APIView):

    @swagger_auto_schema(request_body=ResetPasswordEmailSerializer)
    def post(self, request):
        serializer = ResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            try:
                user = CustomUser.objects.get(email=email)
                user.generate_otp()
                user.send_password_reset_email()
                return Response({"success": True}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"success": False, "message": "The account was not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckCodeView(APIView):
    @swagger_auto_schema(request_body=CheckCodeSerializer)
    def post(self, request):
        serializer = CheckCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordView(APIView):
    @swagger_auto_schema(request_body=ConfirmPasswordSerializer)
    def post(self, request):
        serializer = ConfirmPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            new_password = serializer.validated_data.get('new_password')
            user = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            # user.last_otp = None
            # user.otp_expiry = None
            user.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# blocking views
class BlockCreateView(generics.CreateAPIView):
    """
    View for listing all block relationships or creating a new block relationship.

    Only authenticated users can access this view.
    """
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsBlockerSelf, IsAuthenticated]

  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"success": True, "message": "Block relationship created successfully."}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            message = e.detail if isinstance(e.detail, str) else ' '.join([str(item) for sublist in e.detail.values() for item in sublist])
            return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save()


class BlockListView(generics.ListAPIView):
    """
    View for listing all block relationships.

    Only authenticated users can access this view.
    """
    serializer_class = BlockListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns blocks for the authenticated user.
        """
        user = self.request.user
        return Block.objects.filter(blocker=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True,  context={'request': request})
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class UnblockUserView(generics.DestroyAPIView):
    """
    View for unblocking a user.

    Only authenticated users can access this view.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        blocker = request.user
        blocked_id = kwargs.get('blocked_id')

        # Fetch the block relationship to delete
        block = get_object_or_404(Block, blocker=blocker, blocked_id=blocked_id)

        # Delete the block relationship
        block.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

