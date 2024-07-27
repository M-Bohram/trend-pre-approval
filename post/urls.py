from django.urls import path

from .views import (
    PostList, PostDetail,
    CommentList, CommentDetail,
    LikeToggleView,
    PostComments, CreatePost, CreateComment, HideorUnhidePostView,
    PostLikersList)


urlpatterns = [
    # posts endpoints
    path('post/createpost/', CreatePost.as_view(), name='create_post'),
    path('post/', PostList.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    # comments endpoints
    path('post/createcomment/', CreateComment.as_view(), name='create_comment'),
    path('post/<int:pk>/comments/', PostComments.as_view(), name='post_comments'),
    path('post/<int:post_id>/comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    path('post/comments/', CommentList.as_view(), name='comment-list'),


    # likes endpoints
    path('post/<int:pk>/likers/', PostLikersList.as_view(), name='post-likers-list'),
    path('post/toggle-like/', LikeToggleView.as_view(), name='toggle-like'),

    path('post/hide-or-unhide-post/', HideorUnhidePostView.as_view(), name='hide-post'),
]