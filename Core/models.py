from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    # current user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()

    # personal statement
    bio = models.TextField(blank=True)

    # avatar
    profile_img = models.ImageField(upload_to="profile_images", default="blank_profile_image.png")

    # location
    location = models.CharField(max_length=100, blank=True)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # user id
    user = models.CharField(max_length=100)

    # image posted
    image = models.ImageField(upload_to="post_images")

    # post title
    caption = models.TextField()
    created_time = models.DateTimeField(default=datetime.now)

    # likes
    count_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    # post id
    post_id = models.CharField(max_length=500)

    # user id
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowerCount(models.Model):
    # follower
    follower = models.CharField(max_length=100)

    # user
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user



