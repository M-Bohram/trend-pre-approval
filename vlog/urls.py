from django.urls import path
from .views import VideoDetailView, VlogCommentList, VideoComments, VlogLikeToggleView, VideoLikersList, VideoListView, VideoCreateView

urlpatterns = [
    # URL pattern for listing all videos / creating a new video
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/create/', VideoCreateView.as_view(), name='video-create'),
    # URL pattern for retrieving, updating, or deleting a specific video by its ID
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),

    # Comment endpoints
    path('videos/createcomment/', VlogCommentList.as_view(), name='create_comment'),
    path('videos/<int:pk>/comments/', VideoComments.as_view(), name='video_comments'),
   
    # Like endpoints
    path('videos/<int:pk>/likers/', VideoLikersList.as_view(), name='video-likers-list'),
    path('videos/toggle-like/', VlogLikeToggleView.as_view(), name='toggle-like'),
]
