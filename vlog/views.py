from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Video, VlogLike, VlogCommentCounter, VlogLikeCounter
from authentication.pagination import CustomPageNumberPagination
from .serializers import VideoSerializer, VlogComment, VlogCommentSerializer, VlogLikeToggleSerializer, VideoLikersSerializer
from authentication.models import Block, CustomUser


class VideoListView(generics.ListAPIView):
    """
    API view to retrieve list of videos.
    """
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Optionally restricts the returned videos to those not blocked by the author.
        """
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
            blocked_by_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
            users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
            queryset = Video.objects.exclude(author__in=users_to_exclude)
        return queryset.order_by('-created_at')


class VideoCreateView(generics.CreateAPIView):
    """
    API view to create a new video.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Set the author of the video to the currently authenticated user.
        """
        serializer.save(author=self.request.user)


class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a video instance.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]  


class VlogCommentList(generics.ListCreateAPIView):
    """

    API view to create comments for a video,
    method : " POST "
    body : {
        "video_id": "2",
        "content" : "new comment from rania1"
    }
    """
    queryset = VlogComment.objects.all()
    serializer_class = VlogCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def perform_create(self, serializer):
        video_id = self.request.data.get('video_id')
        video = Video.objects.get(id=video_id)
        serializer.save(user=self.request.user, video=video)
        # Update comment counter
        comment_counter, created = VlogCommentCounter.objects.get_or_create(video=video)
        comment_counter.count = video.comment_count()
        comment_counter.save()


class VlogLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VlogLikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        video = validated_data['video_id']

        # user = validated_data['user']

        try:
            # Check if the user has already liked the video
            like = VlogLike.objects.get(video=video, user=request.user)
            # If the user has already liked the video, unlike it
            like.delete()
            # message = "Video unliked successfully."
            liked = False
        except VlogLike.DoesNotExist:
            # If the user has not liked the video, like it
            VlogLike.objects.create(video=video, user=request.user)
            # message = "Video liked successfully."
            liked = True

        # Update like counter (increase/decrease)
        like_counter, created = VlogLikeCounter.objects.get_or_create(video=video)
        like_counter.count = video.like_count()
        like_counter.save()

        return Response({"liked": liked}, status=status.HTTP_200_OK)


class VideoLikersList(generics.ListAPIView):
    """
        List all post Likers.
    """
    serializer_class = VideoLikersSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        video_id = self.kwargs.get('pk')
        request_user = self.request.user
        # Get list of blocked user IDs
        blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
        blocked_by_users = Block.objects.filter(blocked=request_user).values_list('blocker', flat=True)
        users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
        likers_ids = VlogLike.objects.filter(video_id=video_id).values_list('user_id', flat=True).order_by('-created_at')
        return CustomUser.objects.filter(id__in=likers_ids).exclude(id__in=users_to_exclude)


class VideoComments(generics.ListAPIView):
    serializer_class = VlogCommentSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        video_id = self.kwargs['pk']  # Get the video ID from the URL parameter
        request_user = self.request.user
        video = get_object_or_404(Video, pk=video_id)  # Retrieve the videos object

        if not request_user.is_authenticated:
            # Handle case when user is not authenticated
            return VlogComment.objects.none()
        # Get list of blocked user IDs
        blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
        blocked_by_users = Block.objects.filter(blocked=request_user).values_list('blocker', flat=True)
        users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
        return VlogComment.objects.filter(video=video).exclude(user__in=users_to_exclude).order_by('-created_at')