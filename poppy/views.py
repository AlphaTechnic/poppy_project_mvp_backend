import datetime
import smtplib
import os, json
import random
from json import dumps
import requests
from django.shortcuts import HttpResponse
from .models import PetOwner, Post, Fee, Pet, Comment, Application
from haversine import haversine
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from email.mime.text import MIMEText
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import *
from rest_framework.response import Response


def get_distance(coordinate1, coordinate2):
    distance = haversine(coordinate1, coordinate2, unit='km')

    return distance


def get_lat_lng(address):
    result = ""

    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
    rest_api_key = '7d66b3ade18db0422c2f27baada16e45'
    header = {'Authorization': 'KakaoAK ' + rest_api_key}

    r = requests.get(url, headers=header)

    if r.status_code == 200:
        result_address = r.json()["documents"][0]["address"]
        result = float(result_address["x"]), float(result_address["y"])
    else:
        result = "ERROR[" + str(r.status_code) + "]"

    return result


def get_fee_default_eq_0(petowner):
    fee_objs = Fee.objects.filter(owner=petowner.user)
    if len(fee_objs) == 0:
        return 0
    else:
        return fee_objs[0].small[0]


def get_petsitters_nearby(request, address, dist_or_fee):
    coordi_client = get_lat_lng(address)
    if dist_or_fee == 0:
        petowners = PetOwner.objects.all()
            petsitters = sorted(
                petowners, key=lambda petowner: get_distance(coordi_client, get_lat_lng(petowner.address))
            )
        else:
            petsitters = sorted(
                petowners, key=lambda petowner: get_distance(coordi_client, get_lat_lng(petowner.address))
            )[:30]

    elif dist_or_fee == 1:
        petowners = PetOwner.objects.all()
        if len(petowners) <= 30:
            petsitters = sorted(
                petowners, key=lambda petowner: (
                    get_fee_default_eq_0(petowner),
                    get_distance(coordi_client, get_lat_lng(petowner.address))
                )
            )
        else:
            petsitters = sorted(
                petowners, key=lambda petowner: (
                    get_fee_default_eq_0(petowner),
                    get_distance(coordi_client, get_lat_lng(petowner.address))
                )
            )[:30]

    petsitter_list = []
    for petsitter in petsitters:
        info = dict()
        #print(petsitter.user.id, "!!!!!!!!!!!!!!!!!!!!!!!!!")
        info["pk"] = petsitter.user.id
        info["address"] = petsitter.address

        distance = get_distance(coordi_client, get_lat_lng(petsitter.address))
        if distance < 1:
            info["distance"] = str(round(distance * 1000)) + 'm'
        elif 1 <= distance < 10:
            info["distance"] = str(round(distance, 1)) + 'km'
        else:
            info["distance"] = str(round(distance)) + 'km'

        post_objs = Post.objects.filter(owner_id=petsitter.user.id)
        if len(post_objs) != 0:
            post_obj = post_objs[0]
            info["room_img"] = str(post_obj.room_img)
            info["title"] = post_obj.title
        else:
            info["room_img"] = "https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/room_img/default_room.png"
            info["title"] = "https://poppy-mvp.s3.ap-northeast-2.amazonaws.com/room_img/default_room.png"


        comment_info = dict()
        comment_objs = Comment.objects.filter(target_petsitter=petsitter.user).order_by('-posted_date')
        if len(comment_objs) != 0:
            comment_obj = comment_objs[0]
            comment_info["score"] = comment_obj.score
            comment_info["num_of_comments"] = comment_obj.num_of_comments

        info["comment"] = comment_info

        fee_objs = Fee.objects.filter(owner=petsitter.user)
        if len(fee_objs) != 0:
            fee_obj = fee_objs[0]
            info["small_dog_fee"] = fee_obj.small
        else:
            #info["small_dog_fee"] = ""
            continue

        petsitter_list.append(info)

    result = dict()
    result["petsitter_list"] = petsitter_list

    return HttpResponse(dumps(result, ensure_ascii=False), content_type='application/json')


class PetsitterView(APIView):
    def get(self, request, petsitter_pk):
        #print(request.auth)
        petowner_obj = PetOwner.objects.filter(user_id=petsitter_pk)[0]
        post_obj = Post.objects.filter(owner_id=petsitter_pk)[0]
        fee_obj = Fee.objects.filter(owner_id=petsitter_pk)[0]
        pet_objs = Pet.objects.filter(owner_id=petsitter_pk)
        comment_objs = Comment.objects.filter(target_petsitter_id=petsitter_pk)

        info = dict()
        info["room_img"] = post_obj.room_img
        info["name"] = petowner_obj.name
        # info["small_dog_fee"] = list(map(lambda number: format(number, ',') + '원', fee_obj.small))
        # info["middle_dog_fee"] = list(map(lambda number: format(number, ',') + '원', fee_obj.middle))
        # info["large_dog_fee"] = list(map(lambda number: format(number, ',') + '원', fee_obj.large))
        info["small_dog_fee"] = fee_obj.small
        info["middle_dog_fee"] = fee_obj.middle
        info["large_dog_fee"] = fee_obj.large

        info["title"] = post_obj.title
        info["content"] = post_obj.content

        pets = []
        for pet in pet_objs:
            pet_info = dict()

            pet_info["pet_img"] = pet.pet_img
            pet_info["name"] = pet.name
            pet_info["breed"] = pet.breed
            pet_info["age"] = str(pet.age) + "살"
            pet_info["character"] = pet.character
            pets.append(pet_info)
        info["pets"] = pets

        if len(comment_objs) == 0:
            comment_info = dict()

        else:
            comment_info = dict()
            comment_recent = sorted(
                comment_objs, key=lambda comment: comment.posted_date, reverse=True
            )[0]
            comment_info["name"] = PetOwner.objects.get(user=comment_recent.author).name
            comment_info["content"] = comment_recent.content
            comment_info["date"] = comment_recent.posted_date.strftime('%Y. %#m. %d')
            comment_info["score"] = comment_recent.score
            comment_info["num_of_comments"] = comment_recent.num_of_comments

        info["comment"] = comment_info
        info["available_services"] = post_obj.available_services

        return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


# def comment num_of_comments랑 score 계산
#     comment_objs = Comment.objects.filter(target_petsitter=petsitter_pk)
#
#     num_of_comments = len(comment_objs)
#     sum_of_scores = 0
#     for comment_obj in comment_objs:
#         sum_of_scores += comment_obj.score
#     avg = sum_of_scores / num_of_comments
#
#     comment_info["score"] = round(avg, 1)
#     comment_info["num_of_comments"] = num_of_comments

def is_phone_num_authenticated(phone_num):
    try:
        phone_num_int = int(phone_num)
    except:
        return False
    else:
        if len(phone_num) != 11:
            return False
        if phone_num[:3] != '010':
            return False
        return True


class ApplyView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        sender_pk = request.user.id
        target_petsitter_pk = data['target_petsitterID']
        phone_num = data['phone_num']
        pet_breed = data['pet_breed']
        pet_size = data['pet_size']
        start_time = data['start_time']
        end_time = data['end_time']
        total_fee = data['total_fee']

        # 핸드폰 번호 유효성 검사
        if not is_phone_num_authenticated(phone_num):
            return HttpResponse('no 휴대폰 번호가 유효하지 않음')

        # 입력 날짜 유효성 검사. 펫시터의 돌봄 가능 날짜가 맞는지
        start_day_str = start_time[:10]
        end_day_str = end_time[:10]

        start_day_obj = datetime.datetime.strptime(start_day_str, '%Y-%m-%d').date()
        end_day_obj = datetime.datetime.strptime(end_day_str, '%Y-%m-%d').date()
        available_days = Post.objects.filter(owner_id=target_petsitter_pk)[0].available_days

        while True:
            if start_day_obj.strftime('%Y%m%d') not in \
                    list(map(lambda available_day: available_day.strftime('%Y%m%d'), available_days)):
                return HttpResponse('no 펫시터의 돌봄 가능 날짜에 해당하지 않음')
            if start_day_obj == end_day_obj:
                break
            start_day_obj = start_day_obj + datetime.timedelta(days=1)

        # 저장
        Application.objects.create(
            sender=User.objects.get(id=sender_pk),
            target_petsitter=User.objects.get(id=target_petsitter_pk),
            start_time=datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M'),
            end_time=datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M'),
            phonenum_of_sender=phone_num,
            pet_breed=pet_breed,
            pet_size=pet_size,
            total_fee=total_fee
        )
        return HttpResponse('ok')


##########################################4순위#################################################

class ApplicationView(APIView):
    def get(self, request):
        pass
#         target_petsitter_pk = str(request.user)
#
#         sender = PetOwner.objects.filter(user=User.objects.get(id=sender_pk))[0]
#
#         sender_application = Application.objects.filter(
#             sender=User.objects.get_by_natural_key(sender_pk)
#         ).filter(
#             target_petsitter=User.objects.get_by_natural_key(target_petsitter_pk)
#         )[0]
#
#         info = dict()
#         info["target_petsitter"] = sender.name
#
#         service_list = [sender_application.pet_size, "당일 돌봄"]
#
#         # start_time = sender_application.start_time
#         # end_time = sender_application.end_time
#         # if start_time.date() == end_time.date():
#         #     service_list.append("당일 돌봄")
#
#         info["service"] = service_list
#         locale.setlocale(locale.LC_ALL, '')
#         info["date"] = sender_application.start_time.strftime('%Y년 %m월 %d일')
#         info["total_fee"] = sender_application.total_fee
#
#         return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')

#################################################################


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
secret_file = os.path.join(BASE_DIR, 'secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

@csrf_exempt
def is_authenticated(request):
    data = json.loads(request.body)
    name = data['name']
    email = data['email']

    ## email 전송
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()  # say Hello
    smtp.starttls()  # TLS 사용시 필요
    smtp.login('poppymyneighbor@gmail.com', get_secret("email_password"))

    # 인증코드 생성
    num_list = list(range(1, 10))  # num = [1,2,3,4,5,6,7,8,9]
    char_list = []
    for i in range(97, 123):
        char_list.append(chr(i))

    random_list = []
    for i in range(2):
        random_list.append(str(num_list.pop(num_list.index(random.choice(num_list)))))
    for i in range(4):
        random_list.append(char_list.pop(char_list.index(random.choice(char_list))))
    random.shuffle(random_list)

    code = ''.join(random_list)

    msg = MIMEText(
        "안녕하세요. " + name + "님\n이웃집 뽀삐 입니다.\n\n본인 확인을 위하여 아래의 인증코드를 확인하신 후, 회원 가입 창에 입력하여 주시기 바랍니다.\n\n  인증 번호 : " + code + "\n\n감사합니다."
    )
    msg['Subject'] = '이웃집뽀삐 : 회원가입을 위한 본인 확인 메일입니다.'
    smtp.sendmail('poppymyneighbor@gmail.com', email, msg.as_string())
    smtp.quit()

    info = dict()
    info["code"] = code
    return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


class SignupView(APIView):
    def post(self, request):
        try:
            password1 = request.data['password1']
            password2 = request.data['password2']
            if password1 != password2:
                raise ValueError
            if len(password1) < 8:
                raise ValueError
        except:
            return HttpResponse("wrong password input")

        else:
            # try:
            petowner_objs = PetOwner.objects.filter(email=request.data['email'])
            if len(petowner_objs) != 0:
                return HttpResponse("already exist")

            # user 저장
            user = User.objects.create_user(
                username=request.data['email'],
                password=password1,
            )
            user.save()

            # PetOwner 객체 생성
            PetOwner.objects.create(
                user=user,
                name=request.data['name'],
                email=request.data['email']
            )

            token = Token.objects.create(user=user)

            info = dict()
            info["Token"] = token.key

            return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        petowner_objs = PetOwner.objects.filter(email=email)
        if len(petowner_objs) == 0:
            return HttpResponse("wrong email input")

        petowner_obj = petowner_objs[0]
        pk = petowner_obj.user.id

        user = authenticate(username=request.data['email'], password=request.data['password'])
        User_objs = User.objects.filter(username=user)

        if len(User_objs) == 0:
            return HttpResponse("wrong password input")

        token = Token.objects.filter(user_id=pk)[0]
        info = dict()
        info["Token"] = token.key

        return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


class NameView(APIView):
    @method_decorator(csrf_exempt)
    def get(self, request):
        pk = request.user.id
        name = PetOwner.objects.filter(user_id=pk)[0].name
        info = dict()
        info["name"] = name

        return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


def price_formatting(price):
    # '30,000원' -> 30,000
    return int(price.replace(",", "").replace("원", ""))


class EditProfileView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        petsitter_pk = request.user.id

        Post.objects.filter(owner_id=petsitter_pk).delete()
        Fee.objects.filter(owner_id=petsitter_pk).delete()
        Pet.objects.filter(owner_id=petsitter_pk).delete()

        serializers = PhotoSerializer(data=data['room_img'])
        # print(serializers, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if serializers.is_valid():
            serializers.save()
            Response(serializers.data, status=status.HTTP_201_CREATED)
        Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

        Post.objects.create(
            owner_id=petsitter_pk,
            room_img=data['room_img'],
            title=data['title'],
            content=data['content'],
            available_days=data['available_days'],
            available_services=data['available_services'],
            certificates=data['certificates'],
        )

        Fee.objects.create(
            owner_id=petsitter_pk,
            small=list(map(price_formatting, data['small_dog_fee'])),
            middle=list(map(price_formatting, data['middle_dog_fee'])),
            large=list(map(price_formatting, data['large_dog_fee']))
        )

        Pet.objects.filter(owner_id=petsitter_pk).delete()
        for pet in data['pets']:
            pet_img = pet["pet_img"]
            name = pet["name"]
            breed = pet["breed"]
            age = int(pet["age"].replace("살", ""))
            character = pet["character"]

            Pet.objects.create(
                owner_id=petsitter_pk,
                pet_img=pet_img,
                name=name,
                breed=breed,
                age=age,
                character=character
            )

        return HttpResponse("ok")


class Image(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, format=None):
        serializers = PhotoSerializer(data=request.data)
        #print(serializers, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
