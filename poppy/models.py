from django.db import models
from django.db.models import IntegerField, DateField
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


def default_available_services():
    return {0: "오래 맡겨주세요", 1: "놀이 가능해요", 2: "약 먹일 수 있어요", 3: "목욕 가능해요", 4: "산책 가능해요", 5: "픽업 해드려요"}


class PetOwner(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    e_mail = models.EmailField()
    address = models.CharField(max_length=200)

    profile_img = models.ImageField(default='img/profile_img/profile_default.png', upload_to='img/profile_img')
    room_img = models.ImageField(default='img/room_img/room_default.png', upload_to='img/room_img')

    title = models.CharField(max_length=100)
    content = models.CharField(max_length=2000)

    is_expert = models.BooleanField(default=False)
    available_days = ArrayField(DateField(null=True))
    available_services = JSONField(default=default_available_services)
    certificate = JSONField(default={})

    def __str__(self):
        return self.name

    def num_of_comments(self):
        return Comment.objects.filter(owner=self).count()

    def scores_avg(self):
        comments = Comment.objects.filter(owner=self)
        comments_num = comments.count()
        Sum = 0
        for comment in comments:
            Sum += comment.score
        return Sum / comments_num


class Fee(models.Model):
    owner = models.OneToOneField(PetOwner, on_delete=models.CASCADE, primary_key=True)
    small = ArrayField(IntegerField(default=0), size=2)
    middle = ArrayField(IntegerField(default=0), size=2)
    large = ArrayField(IntegerField(default=0), size=2)


class Pet(models.Model):
    owner = owner = models.ForeignKey(PetOwner, on_delete=models.CASCADE)
    pet_img = models.ImageField(default='img/pet_img/pet_default.png', upload_to='img/pet_img')
    name = models.CharField(max_length=200)
    breed = models.CharField(max_length=100)
    age = models.IntegerField(default=0)
    character = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Comment(models.Model):
    owner = models.ForeignKey(PetOwner, related_name='comments', on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    posted_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(default=5.0)

    def __str__(self):
        return self.content[:15] + '.. -> ' + str(self.owner)
