import os
from django.conf import settings
from authentication.models import CustomUser
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files import File
from PIL import Image
from moviepy.editor import VideoFileClip
import tempfile
import requests


def validate_video_size(file):
    """
    Validate the size of the uploaded video file.

    Args:
        file (UploadedFile): The uploaded video file.

    Raises:
        ValidationError: If the file size exceeds 200 MB.
    """
    max_size = 200 * 1024 * 1024  # 200 MB
    if file.size > max_size:
        raise ValidationError(f"File size should not exceed {max_size / (1024 * 1024)} MB.")


def validate_video_duration(duration):
    """
    Validate the duration of the uploaded video.

    Args:
        duration (timedelta): The duration of the video.

    Raises:
        ValidationError: If the video duration exceeds 3 minutes.
    """
    max_duration = timezone.timedelta(seconds=15)
    if duration > max_duration:
        raise ValidationError(f"Video duration should not exceed {max_duration}.")


def generate_thumbnail(video_path, thumbnail_path):

    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(1)  # Extract frame at 1 second
    image = Image.fromarray(frame)
    # image.save(os.path.join(settings.MEDIA_ROOT, thumbnail_path))  # locally
    image.save(thumbnail_path) # with S3


class Video(models.Model):
    """
    Model representing a video.

    Attributes:
        author (ForeignKey): The user who uploaded the video.
        title (CharField): The title of the video.
        description (TextField): The description of the video.
        video (FileField): The uploaded video file.
        duration (DurationField): The duration of the video.
        created_at (DateTimeField): The date and time when the video was created.
        updated_at (DateTimeField): The date and time when the video was last updated.
    """
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video = models.FileField(
        upload_to='vlogs/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi']),
            validate_video_size
        ]
    )
    duration = models.DurationField(
        null=True,
        blank=True,
        validators=[validate_video_duration]
    )
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Save the video instance and calculate its duration using moviepy.

        If a video file is uploaded, the method saves the file, calculates its duration using moviepy,
        sets the duration field, validates the duration, and saves the model instance.

        If no video file is uploaded, the method saves the model instance without any video processing.
        """
        is_new = not self.pk  # Check if the video is being created for the first time
        with transaction.atomic():
            super().save(*args, **kwargs)  # Save the video instance to generate the pk

        if self.video and is_new:
            # video_path = os.path.join(settings.MEDIA_ROOT, self.video.name)  # locally
            # Download the video file from S3
            video_url = self.video.url
            with tempfile.NamedTemporaryFile(delete=False) as temp_video:
                temp_video.write(requests.get(video_url).content)
                temp_video_path = temp_video.name

            video = VideoFileClip(temp_video_path)
            duration_seconds = video.duration
            self.duration = timezone.timedelta(seconds=duration_seconds)
            validate_video_duration(self.duration)

            # Generate thumbnail
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'video_thumbnails', f'{self.pk}.jpg')
            generate_thumbnail(temp_video_path, thumbnail_path)
            self.thumbnail.save(f'{self.pk}.jpg', File(open(thumbnail_path, 'rb')))
            video.close()

            # Remove the temporary video file
            os.remove(temp_video_path)
            # Save the model instance with the updated duration and thumbnail
            super().save(update_fields=['duration', 'thumbnail'])

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title


class VlogComment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vlog_comments')
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."


class VlogLike(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vlog_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')

    def __str__(self):
        return f"{self.user.username} liked video {self.video.id}"


class VlogLikeCounter(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)


class VlogCommentCounter(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
