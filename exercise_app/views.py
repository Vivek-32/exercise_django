from django.shortcuts import render, HttpResponse
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.middleware import csrf
from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.permissions import  IsAuthenticated, AllowAny, BasePermission
from django.views.decorators.csrf import csrf_exempt
from .models import Country, State, City, CustomUser
from .serializers import UserSerializer, CountrySerializer, StateSerializer, CitySerializer
from .constants import INSERT_ONE_DATA, INSERT_MANY_DATA
from .authenticate import CustomAuthentication, create_access_token, create_refresh_token

class UserListPagination(CursorPagination):
    ordering = '-date_joined'

class SignInAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny] 

    def get_tokens(self, user):
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def authenticate_user(self, username, password=None):
        user = get_user_model().objects.get(username=username)
        if check_password(password, user.password):
            return user
        else: 
            return None

    def create(self, request, *args, **kwargs):
        response = Response()
        username = request.data.get('username')
        password = request.data.get('password')
        user = self.authenticate_user(username=username, password=password)
        if user:
            login(request, user)
            data = self.get_tokens(user)
            response.set_cookie(key='access_token', value=data['access_token'])
            response.set_cookie(key='refresh_token', value=data['refresh_token'])
            response.set_cookie(key='user_id', value=user.id)
            data['csrf_token'] =  csrf.get_token(request)
            response.data = {"Success" : "Login successfully","data":data}  
            return response
        
        return Response({'detail': 'Invaild credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SignoutAPIView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]
    authentication_classes=[CustomAuthentication]
    print('jvhkj')
    def get(self, request, *args, **kwargs):
        response = Response()
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('user_id')
        response.data = {'detail': 'Successfully logged out'}
        response.status_code = status.HTTP_200_OK
        logout(request)
        return response

class UserListAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserListPagination
    # permission_classes=[IsAuthenticated]
    authentication_classes=[CustomAuthentication]

    def create(self, request, *args, **kwargs):
        request.data['password'] = make_password(request.data['password'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes=[IsAuthenticated]


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.my_user == request.user
    

class CountryCreateListView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes=[IsAuthenticated, IsOwner]
    # authentication_classes=[CustomAuthentication]
    
    def create(self, *args, **kwargs):

        user = get_user_model().objects.get(id=self.request.COOKIES['user_id'])
        data = self.request.data
        data['my_user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CountryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated, IsOwner]

# def insert(request):
#     # country = INSERT_ONE_DATA['country']
#     # state = INSERT_ONE_DATA['state']
#     # city = INSERT_ONE_DATA['city']

#     country = request.data['country']
#     state = request.data['state']
#     city = request.data['city']
#     user_id = request.COOKIES.get('user_id')
#     response = Response()

#     if country:
#         name = country['name']
#         country_code = country['country_code']
#         curr_symbol = country['curr_symbol']
#         phone_code = country['phone_code']
#         insert_country = Country.objects.create(name=name, country_code=country_code, curr_symbol=curr_symbol, phone_code=phone_code,my_user=user_id)
#         response.data['country'] = insert_country

#     if state:
#         name = state['name']
#         state_code = state['state_code']
#         gst_code = state['gst_code']
#         insert_state = State.objects.create(name=name, state_code=state_code, gst_code=gst_code, country=insert_country)
#         response.data['state'] = insert_state


#     if city:
#         name = city['name']
#         city_code = city['city_code']
#         phone_code = city['phone_code']
#         population = city['population']
#         avg_age = city['avg_age']
#         num_of_adult_males = city['num_of_adult_males']
#         num_of_adult_females = city['num_of_adult_females']
#         insert_city = City.objects.create(name=name, city_code=city_code, phone_code=phone_code, population=population, avg_age=avg_age, num_of_adult_males=num_of_adult_males, num_of_adult_females=num_of_adult_females, state=insert_state)
#         response.data['city'] = insert_city

#     response['status_code'] = status.HTTP_201_CREATED
#     return response
    
# @csrf_exempt
# def bulk_insert(request):
#     country = INSERT_MANY_DATA['country']
#     state = INSERT_MANY_DATA['state']
#     city = INSERT_MANY_DATA['city']

#     if country:
#         country_data = []
#         for data in country:
#             name = data['name']
#             country_code = data['country_code']
#             curr_symbol = data['curr_symbol']
#             phone_code = data['phone_code'] 
#             country_data.append(Country(name=name, country_code=country_code, curr_symbol=curr_symbol, phone_code=phone_code))

#         Country.objects.bulk_create(country_data)


#     if state:
#         state_data  = []
#         for data in state:
#             name = data['name']
#             state_code = data['state_code']
#             gst_code = data['gst_code']
#             country_id = Country.objects.get(country_code=data['country_code'])
#             state_data.append(State(name=name, state_code=state_code, gst_code=gst_code, country=country_id))

#         State.objects.bulk_create(state_data)

#     if city:
#         city_data = []
#         for data in city:
#             name = data['name']
#             city_code = data['city_code']
#             phone_code = data['phone_code']
#             population = data['population']
#             avg_age = data['avg_age']
#             num_of_adult_males = data['num_of_adult_males']
#             num_of_adult_females = data['num_of_adult_females']
#             state_id = State.objects.get(state_code=data['state_code'])
#             city_data.append(City(name=name, city_code=city_code, phone_code=phone_code, population=population, avg_age=avg_age, num_of_adult_males=num_of_adult_males, num_of_adult_females=num_of_adult_females, state=state_id))
        
#         City.objects.bulk_create(city_data)

#     return HttpResponse("Bulk data insert successfully")

# @csrf_exempt
# def bulk_update(request):
#     Country.objects.filter(name='Canada').update(curr_symbol='¥')
#     State.objects.filter(name='Ontario').update(gst_code='GST2_')
#     City.objects.filter(name='Toronto').update(avg_age=30.0)
#     return HttpResponse("Bulk data updated successfully")

# @csrf_exempt
# def fetch_all(request):
#     country = Country.objects.all().values()
#     state = State.objects.all().values()
#     city  = City.objects.all().values()
#     print('{} {} {}'.format(country, state, city))
#     return HttpResponse("Fetched data successfully")


# @csrf_exempt
# def fetch_all_cities_specific_state(request):
#     state_cities = City.objects.filter(state__name='Odisha').values()
#     print(state_cities)
#     return HttpResponse("Fetched data successfully")

# @csrf_exempt
# def fetch_all_state_specific_country(request):
#     country_state = State.objects.filter(country__name='India').values()
#     print(country_state)
#     return HttpResponse("Fetched data successfully")

# @csrf_exempt
# def fetch_all_cities_specific_Country(request):
#     country_cities = City.objects.filter(state__country__name='India').values()
#     print(country_cities)
#     return HttpResponse("Fetched data successfully")

# @csrf_exempt
# def fetch_max_min_population(request):
#     min_population_city = City.objects.filter(state__country__name='India').values().order_by('population').first()
#     max_population_city = City.objects.filter(state__country__name='India').values().order_by('-population').first()    
#     print(min_population_city)
#     print(max_population_city)
#     return HttpResponse("Fetched data successfully")