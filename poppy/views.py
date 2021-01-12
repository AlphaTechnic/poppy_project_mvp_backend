import datetime
import locale
from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate
from .models import PetOwner, Post, Fee, Pet, Comment, Application
from django.contrib.auth.models import User
from django.utils import timezone
from random import choice
from json import dumps
import requests
from haversine import haversine


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


def get_petsitters_nearby(request, address, dist_or_fee):
    coordi_client = get_lat_lng(address)
    if dist_or_fee == 0:
        petowners = PetOwner.objects.all()

        if len(petowners) <= 30:
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
                    Fee.objects.get(owner=petowner.user).small[0],
                    get_distance(coordi_client, get_lat_lng(petowner.address))
                )
            )
        else:
            petsitters = sorted(
                petowners, key=lambda petowner: (
                    Fee.objects.get(owner=petowner.user).small[0],
                    get_distance(coordi_client, get_lat_lng(petowner.address))
                )
            )[:30]

    petsitter_list = []
    for petsitter in petsitters:
        info = dict()
        info["address"] = petsitter.address

        distance = get_distance(coordi_client, get_lat_lng(petsitter.address))
        if distance < 1:
            info["distance"] = str(round(distance * 1000)) + 'm'
        elif 1 <= distance < 10:
            info["distance"] = str(round(distance, 1)) + 'km'
        else:
            info["distance"] = str(round(distance)) + 'km'

        post_obj = Post.objects.get(owner=petsitter.user)
        info["room_img"] = post_obj.room_img
        info["title"] = post_obj.title

        comment_obj = Comment.objects.get(target_petsitter=petsitter.user)
        info["score"] = comment_obj.score
        info["num_of_comments"] = comment_obj.num_of_comments

        fee_obj = Fee.objects.get(owner=petsitter.user)
        info["small_dog_fee"] = fee_obj.small

        petsitter_list.append(info)

    result = dict()
    result["petsitter_list"] = petsitter_list

    return HttpResponse(dumps(result, ensure_ascii=False), content_type='application/json')


def petsitter_detail(request, petsitterID):
    petowner_obj = PetOwner.objects.filter(user=User.objects.get_by_natural_key(petsitterID))[0]
    post_obj = Post.objects.filter(owner=User.objects.get_by_natural_key(petsitterID))[0]
    fee_obj = Fee.objects.filter(owner=User.objects.get_by_natural_key(petsitterID))[0]
    pet_objs = Pet.objects.filter(owner=User.objects.get_by_natural_key(petsitterID))
    comment_objs = Comment.objects.filter(target_petsitter=User.objects.get_by_natural_key(petsitterID))

    info = dict()
    info["room_img"] = post_obj.room_img
    info["name"] = petowner_obj.name
    info["small_dog_fee"] = list(map(lambda number: format(number, ',')+'원', fee_obj.small))
    info["middle_dog_fee"] = list(map(lambda number: format(number, ',')+'원', fee_obj.middle))
    info["large_dog_fee"] = list(map(lambda number: format(number, ',')+'원', fee_obj.large))

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

    comment_recent = sorted(
        comment_objs, key=lambda comment: comment.posted_date, reverse=True
    )[0]
    comment_info = dict()

    comment_info["name"] = PetOwner.objects.get(user=comment_recent.author).name
    comment_info["content"] = comment_recent.content
    comment_info["date"] = comment_recent.posted_date.strftime('%Y. %#m. %d')
    comment_info["score"] = comment_recent.score
    comment_info["num_of_comments"] = comment_recent.num_of_comments
    info["comment"] = comment_info

    info["available_services"] = post_obj.available_services
    return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')


# def comment num_of_comments랑 score 계산
#     comment_objs = Comment.objects.filter(target_petsitter=User.objects.get_by_natural_key(petsitterID))
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
    if type(phone_num) != int:
        return False
    if len(phone_num) != 11:
        return False
    if str(phone_num)[:3] != '010':
        return False
    return True


def apply(request):
    senderID = request.POST['senderID']
    target_petsitterID = request.POST['target_petsitterID']
    phone_num = request.POST['phone_num']
    pet_breed = request.POST['pet_breed']
    pet_size = request.POST['pet_size']
    start_time = request.POST['start_time']
    end_time = request.POST['end_time']
    total_fee = request.POST['total_fee']

    # 핸드폰 번호 유효성 검사
    if is_phone_num_authenticated(phone_num):
        return HttpResponse('no')

    # 입력 날짜 유효성 검사. 펫시터의 돌봄 가능 날짜가 맞는지
    start_day_str = start_time[:10]
    end_day_str = end_time[:10]

    start_day_obj = datetime.datetime.strptime(start_day_str, '%Y-%m-%d')
    end_day_obj = datetime.datetime.strptime(end_day_str, '%Y-%m-%d')
    available_days = Post.objects.filter(owner=User.objects.get_by_natural_key(target_petsitterID))

    while True:
        if start_day_obj not in available_days:
            return HttpResponse('no')
        if start_day_obj == end_day_obj:
            break

    # 저장
    Application.objects.create(
        sender=User.objects.get_by_natural_key(senderID),
        target_petsitter=User.objects.get_by_natural_key(target_petsitterID),
        start_time=datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M'),
        end_time=datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M'),
        phonenum_of_sender=phone_num,
        pet_breed=pet_breed,
        pet_size=pet_size,
        total_fee=total_fee
    )
    return HttpResponse('ok')


def care_detail(request, senderID, target_petsitterID):
    sender = PetOwner.objects.filter(user=User.objects.get_by_natural_key(senderID))[0]

    sender_application = Application.objects.filter(
        sender=User.objects.get_by_natural_key(senderID)
    ).filter(
        target_petsitter=User.objects.get_by_natural_key(target_petsitterID)
    )[0]

    info = dict()
    info["target_petsitter"] = sender.name

    service_list = [sender_application.pet_size, "당일 돌봄"]

    # start_time = sender_application.start_time
    # end_time = sender_application.end_time
    # if start_time.date() == end_time.date():
    #     service_list.append("당일 돌봄")

    info["service"] = service_list
    locale.setlocale(locale.LC_ALL, '')
    info["date"] = sender_application.start_time.strftime('%Y년 %m월 %d일')
    info["total_fee"] = sender_application.total_fee

    return HttpResponse(dumps(info, ensure_ascii=False), content_type='application/json')