'''
URL Patterns Documentation

These are the URL patterns for our project's API endpoints.

Attributes:
    MyTokenObtainPairSerializer: URL pattern for user authentication.
    TokenRefreshView: URL pattern for token refresh.
    UserRegisterView: URL pattern for user registration.
    DisplayList: URL pattern for displaying a list of users and creating new users.
    DisplayDetail: URL pattern for displaying, updating, and deleting individual user instances.

Usage:
    These URL patterns define endpoints for user authentication, registration, and CRUD operations on user instances.

    Example usage in urls.py:

    urlpatterns = [
        path('login/', MyTokenObtainPairView.as_view(), name='login'),
        path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('register/', UserRegisterView.as_view(), name='register'),
        path('users/', DisplayList.as_view(), name='users_list_create'),
        path('users/<int:pk>/', DisplayDetail.as_view(), name='user_detail'),
    ]

    Example Data:

    1. path('login/', MyTokenObtainPairSerializer.as_view(), name='login'):
        Endpoint for user login and obtaining an access token and a refresh token.

        Example Request: POST /login/ (with username and password in the request body)

        Example Response: {
            "refresh": "refresh_token",
            "access": "access_token",
            "user": "username",
            "id": user_id,
            "avatar": "avatar_url",
            "is_staff": is_staff,
            "is_active": is_active,
            "phone_number": "phone_number",
            "profile_id": profile_id
        }


    2. Token Refresh:
       - Endpoint: `/api/login/refresh/`
       - Method: `POST`

       - Example Request Body:
         ```json
         {
             "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
         }
         ```

       - Example Response (Successful Refresh):
         ```json
         {
             "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
             "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
         }
         ```

    3. User Registration:
       - Endpoint: `/api/register/`
       - Method: `POST`
       - Example Request Body:
         ```json
         {
             "username": "new_user",
             "email": "new_user@example.com",
             "password": "new_password",
             "password2": "new_password",
             "avatar": "<base64_encoded_image_data>" 
         }
         ```
       - Example Response (Successful Registration):
         ```json
         {
             "response": "Successfully registered new user.",
             "email": "new_user@example.com",
             "username": "new_user",
             "avatar": "http://example.com/media/images/avatar.png"
         }
         ```

    4. path('users/', DisplayList.as_view(), name='users'):
        Endpoint for listing all users and creating a new user.
        Example Request: GET /users/
        Example Response: [
            {
                "count": 5,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": 1,
                        "username": "example username",
                        "email": "example email",
                        "avatar": "http://127.0.0.1:8000/media/images/avatar.png",
                        "password": "pbkdf2_sha256$600000$b...."
                    },,
                        ...
            }
        ]
        Example Request: POST /users/ (with username, email, password, and optional avatar in the request body to create a new user)
        Example Response: {
            "id": new_user_id,
            "username": "new_username",
            "email": "new_user@example.com",
            "avatar": "new_avatar_url"
        }

    5. User Detail:
       - Endpoint: `/api/users/<user_id>/`
       - Method: `GET` (to retrieve user details) / `PUT` (to update user details) / `DELETE` (to delete user)
       - Example Response (User Detail):
         ```json
         {
             "id": 1,
             "username": "example_user",
             "email": "example_user@example.com",
             "avatar": "http://example.com/media/images/avatar.png",
             "is_staff": false,
             "is_active": true,
             "password": "pbkdf2_sha256$6..............."
         }
         ```
'''

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairSerializer, DisplayList, DisplayDetail, PasswordResetRequestView, CheckCodeView, ConfirmPasswordView, UserRegisterView, BlockCreateView, BlockListView, UnblockUserView

urlpatterns = [
    path('login/', MyTokenObtainPairSerializer.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegisterView.as_view(), name='register'),
    # reset-password endpoints 
    path('forget-password/', PasswordResetRequestView.as_view(), name='forget-password'),
    path('check-code/', CheckCodeView.as_view(), name='check-code'),
    path('confirm-password/', ConfirmPasswordView.as_view(), name='confirm-password'),
    # path('users/', DisplayList.as_view(), name='users'), 
    # path('users/<int:pk>/', DisplayDetail.as_view(), name='users'),


    # URL pattern for listing all block relationships or creating a new block relationship
    path('blocks/', BlockCreateView.as_view(), name='block-list-create'),
    path('block-list/', BlockListView.as_view(), name='block-list'),
    # URL pattern for retrieving or deleting a specific block relationship
    path('blocks/<int:blocked_id>/', UnblockUserView.as_view(), name='unblock-user'),

]