from django.db import models
from django.utils import timezone
from django.conf import settings
from multiselectfield import MultiSelectField
from django_better_admin_arrayfield.models.fields import ArrayField


class PetOwner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, blank=True, default=' ')
    email = models.EmailField(blank=True, unique=True)
    address = models.CharField(max_length=200, blank=True, default='서울시')

    # def __str__(self):
    #     return self.user

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
        ("장기 예약", "장기 예약"),
        ("실내 놀이", "실내 놀이"),
        ("약물 복용", "약물 복용"),
        ("목욕 가능", "목욕 가능"),
        ("산책 가능", "산책 가능"),
        ("집앞 픽업", "집앞 픽업"),
    )


class Post(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    profile_img = models.ImageField(
        default="https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/profile_img/default_profile.png",
        upload_to='https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/profile_img'
    )
    room_img = models.ImageField(
        default='https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/room_img/default_room.png',
        upload_to='https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/room_img'
    )

    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)

    available_days = ArrayField(models.DateField(null=True, blank=True))
    available_services = MultiSelectField(choices=default_available_services)
    certificates = ArrayField(
        ArrayField(models.CharField(max_length=200), size=3),
        default=list,
        null=True, blank=True
    )

    def __str__(self):
        return str(self.owner) + " : " + str(self.title)


class Fee(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    small = ArrayField(models.IntegerField(default=30000), size=2)
    middle = ArrayField(models.IntegerField(), size=2)
    large = ArrayField(models.IntegerField(), size=2)

    def __str__(self):
        return str(self.owner) + "'s Fee"


class Pet(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pet_img = models.ImageField(
        default='https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/pet_img/default_pet.png',
        upload_to='https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/pet_img'
    )
    name = models.CharField(max_length=200)
    breed = models.CharField(max_length=100)
    age = models.IntegerField(default=0)
    character = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.owner) + "'s Pet"


class Comment(models.Model):
    target_petsitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications_as_target_petsitter', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    posted_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications_as_author', on_delete=models.CASCADE)
    score = models.FloatField(default=5.0)
    num_of_comments = models.IntegerField(default=0)

    def __str__(self):
        return str(self.author) + ' -> ' + str(self.target_petsitter) + " : " + str(self.content[:8])


dog_sizes = (
    ("소형견", "소형견"),
    ("중형견", "중형견"),
    ("중형견", "대형견"),
)


class Application(models.Model):
    is_ongoing = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications_as_sender', on_delete=models.CASCADE)
    target_petsitter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications_as_petsitter', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    phonenum_of_sender = models.CharField(max_length=11)

    pet_breed = models.CharField(max_length=100)
    pet_size = models.CharField(max_length=10, choices=dog_sizes)

    total_fee = models.IntegerField()

    def __str__(self):
        return str(self.sender) + ' -> ' + str(self.target_petsitter)


class test(models.Model):
    testfield = models.CharField(max_length=200)
    photo = models.FileField()
    def __str__(self):
        return self.testfield