import os
from rest_framework import serializers
from .models import Video, VlogComment
import tempfile
from moviepy.editor import VideoFileClip
from rest_framework.exceptions import ValidationError
from profile_app.serializers import ProfileSerializer
from authentication.models import CustomUser


class VideoSerializer(serializers.ModelSerializer):
    custom_user_id = serializers.ReadOnlyField(source='author.id')
    profile_id = serializers.ReadOnlyField(source='author.profile.id')
    avatar = serializers.ImageField(source='author.avatar', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    liked = serializers.SerializerMethodField()
    video_thumb = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'custom_user_id', 'profile_id', 'username', 'avatar', 'description', 'video', 'duration', 'created_at', 'updated_at', 'like_count', 'comment_count', 'liked', 'video_thumb']

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_video_thumb(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
    
    def validate_video(self, video):
        with tempfile.NamedTemporaryFile(delete=False) as temp_video:
            for chunk in video.chunks():
                temp_video.write(chunk)
            temp_video_path = temp_video.name

        try:
            video_clip = VideoFileClip(temp_video_path)
            duration_seconds = video_clip.duration
            if duration_seconds > 15:
                raise ValidationError("Video duration exceeds the maximum allowed duration of 15 seconds.")
        finally:
            video_clip.close()
            os.remove(temp_video_path)

        return video


class VlogCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    custom_user_id = serializers.ReadOnlyField(source='user.id')
    profile_id = serializers.ReadOnlyField(source='user.profile.id')
    avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = VlogComment
        fields = ('id', 'custom_user_id', 'profile_id', 'username','avatar', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'custom_user_id', 'created_at', 'updated_at')


class VlogLikeToggleSerializer(serializers.Serializer):
    video_id = serializers.PrimaryKeyRelatedField(queryset=Video.objects.all())



class VideoLikersSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('profile',)