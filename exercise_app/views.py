from django.shortcuts import render, HttpResponse
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.permissions import  IsAuthenticated, AllowAny, BasePermission
from django.views.decorators.csrf import csrf_exempt
from .models import Country, State, City, CustomUser
from .serializers import UserSerializer, CountrySerializer, StateSerializer, CitySerializer
from .constants import INSERT_ONE_DATA, INSERT_MANY_DATA
from .authenticate import IsOwner

class UserListPagination(CursorPagination):
    ordering = '-date_joined'

class SignInAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny] 

    def get_tokens(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token)
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
            response.data = {"Success" : "Login successfully","data":data}  
            return response
        
        return Response({'detail': 'Invaild credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SignoutAPIView(generics.GenericAPIView):
    permission_classes=(IsAuthenticated,)

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
    permission_classes=[IsAuthenticated]

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
    

class CountryCreateListView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [JWTAuthentication]

    def create(self, *args, **kwargs):
        user = get_user_model().objects.get(id=self.request.COOKIES['user_id'])
        data = self.request.data
        data['my_user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        user = get_user_model().objects.get(id=request.COOKIES['user_id'])
        country = Country.objects.all().filter(my_user=user.id)
        serializer = CountrySerializer(country, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CountryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [JWTAuthentication]

    def get_object(self, request, pk):
        try:
            user_id = int(request.COOKIES['user_id'])
            country =  Country.objects.get(pk=pk)
            if country.my_user.id == user_id:
                return country
            else:
                raise PermissionDenied(detail='You are not allowed to access this data', code=status.HTTP_401_UNAUTHORIZED) 
        except Country.DoesNotExist:
                raise PermissionDenied(detail='Country not found', code=status.HTTP_401_UNAUTHORIZED) 

    def get(self, request, pk):
        country = self.get_object(request, pk)
        serializer = CountrySerializer(country)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def patch(self, request, pk):
        country = self.get_object(request, pk)
        serializer = CountrySerializer(country, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        country = self.get_object(request, pk)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        

class StateCreateListView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def verify_user(self, request, country_code):
        user_id = int(request.COOKIES['user_id'])
        country =  Country.objects.get(country_code=country_code)
        if country.my_user.id == user_id:
            return country
        else:
            raise PermissionDenied(detail='You are not allowed to access this data', code=status.HTTP_401_UNAUTHORIZED) 

    def create(self, request, *args, **kwargs):
        data = request.data
        country = self.verify_user(request=request, country_code=data['country_code'])
        data['country'] = country.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        user_id = request.COOKIES['user_id']
        country = Country.objects.get(my_user=user_id)
        self.verify_user(request=request, country_code=country.country_code)
        state = State.objects.all().filter(country=country.id)
        serializer = StateSerializer(state, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class StateDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, request, pk):
        try:
            user_id = int(request.COOKIES['user_id'])
            state = State.objects.get(pk=pk)
            country_user_id = Country.objects.get(id=state.country.id).my_user.id
            if country_user_id == user_id:
                return state
            else:
                raise PermissionDenied(detail='You are not allowed to access this data', code=status.HTTP_401_UNAUTHORIZED) 
        except State.DoesNotExist:
            raise PermissionDenied(detail='State not found', code=status.HTTP_404_NOT_FOUND) 

    def get(self, request, pk):
        state = self.get_object(request, pk)
        serializer = StateSerializer(state)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        state = self.get_object(request, pk)
        serializer = StateSerializer(state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        state = self.get_object(request, pk)
        state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def verify_user(self, request, state_code):
        user_id = int(request.COOKIES['user_id'])
        state = State.objects.get(state_code=state_code)
        if user_id == state.country.my_user.id:
            return state
        else:
            raise PermissionDenied(detail='You are not allowed to access this data', code=status.HTTP_401_UNAUTHORIZED) 

    def create(self, request):
        data = request.data
        state = self.verify_user(request, data['state_code'])
        data['state'] = state.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        user_id = request.COOKIES['user_id']
        city = City.objects.filter(state__country__my_user=user_id)
        self.verify_user(request=request, state_code=city[0].state.state_code)
        serializer = CitySerializer(city, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CityDetailView(generics.RetrieveDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, request, pk):
        try:   
            user_id = int(request.COOKIES['user_id'])
            city = City.objects.get(pk=pk)
            city_user_id = city.state.country.my_user.id
            if city_user_id == user_id:
                return city
            else:
                raise PermissionDenied(detail='You are not allowed to access this data', code=status.HTTP_401_UNAUTHORIZED) 
        except City.DoesNotExist:
            raise PermissionDenied(detail='State not found', code=status.HTTP_404_NOT_FOUND) 

    def get(self, request, pk):
        city = self.get_object(request, pk)
        serializer = CitySerializer(city)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def patch(self, request, pk):
        city = self.get_object(request, pk)
        serializer = CitySerializer(city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def delete(self, request, pk):
        city = self.get_object(request, pk)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


        
        



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