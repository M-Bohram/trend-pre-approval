from rest_framework import serializers
from authentication.models import CustomUser
from .models import Post, Comment, HiddenPost
from profile_app.serializers import ProfileSerializer


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    custom_user_id = serializers.ReadOnlyField(source='user.id')
    profile_id = serializers.ReadOnlyField(source='user.profile.id')
    avatar = serializers.ImageField(source='user.avatar')

    class Meta:
        model = Comment
        fields = ('id', 'custom_user_id', 'profile_id', 'username', 'avatar', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'custom_user_id', 'created_at', 'updated_at')


class PostSerializer(serializers.ModelSerializer):
    custom_user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.CharField(source='user.username', read_only=True)
    profile_id = serializers.ReadOnlyField(source='user.profile.id')
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    like_counter = serializers.SerializerMethodField()
    comment_counter = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'custom_user_id', 'profile_id', 'username', 'avatar', 'image', 'content', 'created_at', 'updated_at', 'like_counter', 'comment_counter', 'liked')

    def get_username(self, obj):
        return obj.user.username if obj.user else None

    def get_like_counter(self, obj):
        return obj.like_count()

    def get_comment_counter(self, obj):
        return obj.comment_count()

    def get_liked(self, obj):
        request = self.context.get('request')

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class LikeToggleSerializer(serializers.Serializer):
    post_id = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())


class CreatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'image', 'content', 'created_at', 'updated_at')

    def create(self, validated_data):

        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('post', 'user', 'content')


class LikerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('profile',)


class HiddenPostSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = HiddenPost
        fields = ('post_id',)

    def validate_post_id(self, value):
        if not Post.objects.filter(id=value).exists():
            raise serializers.ValidationError("Post does not exist.")
        return value
