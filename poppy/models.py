from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from multiselectfield import MultiSelectField
from django_better_admin_arrayfield.models.fields import ArrayField


class PetOwner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    e_mail = models.EmailField()
    address = models.CharField(max_length=200)

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


default_available_services = (
        (0, "오래 맡겨주세요"),
        (1, "놀이 가능해요"),
        (2, "약 먹일 수 있어요"),
        (3, "목욕 가능해요"),
        (4, "산책 가능해요"),
        (5, "픽업 해드려요"),
    )


class Post(models.Model):
    owner = models.OneToOneField(PetOwner, on_delete=models.CASCADE, primary_key=True)
    profile_img = models.ImageField(default='img/profile_img/profile_default.png', upload_to='img/profile_img')
    room_img = models.ImageField(default='img/room_img/room_default.png', upload_to='img/room_img')

    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)

    available_days = ArrayField(models.DateField(null=True, blank=True))
    available_services = MultiSelectField(choices=default_available_services)
    certificate = ArrayField(
        ArrayField(models.CharField(max_length=200), size=2),
        default=list,
        null=True, blank=True
    )

    def __str__(self):
        return str(self.owner) + " : " + str(self.title)


class Fee(models.Model):
    owner = models.OneToOneField(PetOwner, on_delete=models.CASCADE, primary_key=True)
    small = ArrayField(models.IntegerField(), size=2)
    middle = ArrayField(models.IntegerField(), size=2)
    large = ArrayField(models.IntegerField(), size=2)

    def __str__(self):
        return str(self.owner) + "'s Fee"


class Pet(models.Model):
    owner = models.ForeignKey(PetOwner, related_name='pets', on_delete=models.CASCADE)
    pet_img = models.ImageField(default='img/pet_img/pet_default.png', upload_to='img/pet_img')
    name = models.CharField(max_length=200)
    breed = models.CharField(max_length=100)
    age = models.IntegerField(default=0)
    character = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.owner) + "'s Pet"


class Comment(models.Model):
    target_petsitter = models.ForeignKey(PetOwner, related_name='comments_as_target_petsitter', on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    posted_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(PetOwner, related_name='comments_as_author', on_delete=models.CASCADE)
    score = models.FloatField(default=5.0)

    def __str__(self):
        return self.content[:15] + '.. -> ' + str(self.target_petsitter)


dog_sizes = (
    ("소형견", "소형견"),
    ("중형견", "중형견"),
    ("중형견", "대형견"),
)


class Application(models.Model):
    is_ongoing = models.BooleanField(default=True)
    sender = models.ForeignKey(PetOwner, related_name='applications_as_sender', on_delete=models.CASCADE)
    target_petsitter = models.ForeignKey(PetOwner, related_name='applications_as_receiver', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    phonenum_of_sender = models.BigIntegerField()

    pet_breed = models.CharField(max_length=100)
    pet_size = models.CharField(max_length=10, choices=dog_sizes)

    total_fee = models.IntegerField()

    def __str__(self):
        return str(self.sender) + ' -> ' + str(self.target_petsitter)
