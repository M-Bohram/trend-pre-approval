from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment, LikePost, LikeCounter, HiddenPost, CommentCounter
from rest_framework import generics, status
from rest_framework.response import Response
from authentication.pagination import CustomPageNumberPagination
from .serializers import (CreateCommentSerializer,
                          CreatePostSerializer,
                          PostSerializer,
                          CommentSerializer,
                          LikeToggleSerializer,
                          HiddenPostSerializer,
                          LikerSerializer)
from rest_framework.permissions import IsAuthenticated
from authentication.models import Block, CustomUser


# Create Poset view
class CreatePost(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        # instance = serializer.save()
        # Prepare the response data
        response_data = {
            "id": instance.id,
            "image": instance.image.url,
            "content": instance.content,
            "username": instance.user.username,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# Create Comment view
class CreateComment(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update CommentCounter
        post = serializer.validated_data['post']
        comment_counter, created = CommentCounter.objects.get_or_create(post=post)
        comment_counter.count = post.comment_count()
        comment_counter.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Post views
class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        '''
        Restrict the user from viewing posts if blocked. This means the posts will not be available for liking or commenting, effectively preventing a blocked user from liking or commenting

        The implementation also allows users to hide their own posts, but still be able to access
        those hidden posts themselves. However, other users will not be able to access posts
        that are hidden by other users.
        '''
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
            blocked_by_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
            users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
            # Retrieve IDs of posts hidden by any user
            # hidden_post_ids = HiddenPost.objects.values_list('post_id', flat=True)
            hidden_post_ids = HiddenPost.objects.filter(user=user).values_list('post_id', flat=True)
            queryset = Post.objects.exclude(user__in=users_to_exclude).exclude(id__in=hidden_post_ids)

        return queryset.order_by('-created_at')


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    '''
    creating,updating or deleting a specific post
    '''
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# Comment views
class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


# Post comments view
class PostComments(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        post_id = self.kwargs['pk']  # Get the post ID from the URL parameter
        request_user = self.request.user
        post = get_object_or_404(Post, pk=post_id)  # Retrieve the post object

        if not request_user.is_authenticated:
            # Handle case when user is not authenticated
            return Comment.objects.none()
        # Get list of blocked user IDs
        blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
        blocked_by_users = Block.objects.filter(blocked=request_user).values_list('blocker', flat=True)
        users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))

        # Exclude comments from blocked users
        return Comment.objects.filter(post=post).exclude(user__in=users_to_exclude).order_by('-created_at')


class LikeToggleView(generics.GenericAPIView):
    serializer_class = LikeToggleSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        post = validated_data['post_id']
        user = validated_data['user_id']


        try:
            # Check if the user has already liked the post
            like = LikePost.objects.get(post=post, user=user)
            # If the user has already liked the post, unlike it
            like.delete()
            message = "Post unliked successfully."
            liked = False
        except LikePost.DoesNotExist:
            # If the user has not liked the post, like it
            LikePost.objects.create(post=post, user=user)
            message = "Post liked successfully."
            liked = True
        # Update like counter (increase / decrease)
        like_counter, created = LikeCounter.objects.get_or_create(post=post)
        like_counter.count = post.like_count()
        like_counter.save()

        return Response({"liked": liked}, status=status.HTTP_200_OK)


class PostLikersList(generics.ListAPIView):
    """
        List all post Likers.
    """
    serializer_class = LikerSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        request_user = self.request.user
        # Get list of blocked user IDs
        blocked_users = Block.objects.filter(blocker=request_user).values_list('blocked', flat=True)
        blocked_by_users = Block.objects.filter(blocked=request_user).values_list('blocker', flat=True)
        users_to_exclude = list(set(blocked_users).union(set(blocked_by_users)))
        likers_ids = LikePost.objects.filter(post_id=post_id).values_list('user_id', flat=True).order_by('-created_at')
        return CustomUser.objects.filter(id__in=likers_ids).exclude(id__in=users_to_exclude)

        
class HideorUnhidePostView(generics.GenericAPIView):
    '''
    HideorUnhidePostView allows authenticated users to hide or unhide their own posts.

    Example request data (set method to POST):
        {
            "post_id": 1
        }
        Endpoint: http://127.0.0.1:8000/hide-or-unhide-post/



    Example request data (set method to DELETE):
        {
            "post_id": 1
        }
        Endpoint: http://127.0.0.1:8000/hide-or-unhide-post/
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = HiddenPostSerializer
    allowed_methods = ['POST', 'DELETE']

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        post_id = serializer.validated_data['post_id']
        post = Post.objects.get(id=post_id)
        # Create the hidden post relationship
        HiddenPost.objects.get_or_create(user=user, post=post)
        return Response({"success": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        post_id = serializer.validated_data['post_id']
        post = Post.objects.get(id=post_id)

        HiddenPost.objects.filter(user=user, post=post).delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
