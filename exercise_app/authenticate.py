import jwt, datetime
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.permissions import BasePermission
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import Token
from django.contrib.auth import get_user_model
from config import ACCESS_SECRET_KEY, ACCESS_TOKEN_EXPIRATION,REFRESH_SECRET_KEY,REFRSH_TOKEN_EXPIRATION

def enforce_csrf(request):
    check = CSRFCheck(request)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)    

def check_user(user_id):
    user = get_user_model().objects.get(id=user_id)
    if user:
        return user
    else:
        raise exceptions.NotFound('Invalid User Id')
    
def create_access_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(milliseconds=int(ACCESS_TOKEN_EXPIRATION)),
        'iat': datetime.datetime.utcnow()
    }, ACCESS_SECRET_KEY, algorithm='HS256')

def create_refresh_token(user_id):
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(milliseconds=int(REFRSH_TOKEN_EXPIRATION)),
        'iat': datetime.datetime.utcnow()
    }, REFRESH_SECRET_KEY, algorithm='HS256')

def verify_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms='HS256')
        return payload['user_id']
    except:
        raise exceptions.APIException('Unauthorized')

def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms='HS256')
        return payload['user_id']
    except:
        raise exceptions.APIException('Unauthorized')
    

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access_token') or None
        else:
            raw_token = self.get_raw_token(header)
        
        if raw_token is None:
            return None
        print(raw_token)
        validated_token = self.get_validated_token(raw_token)
        token = request.COOKIES.get('access_token')
        print(validated_token)
        enforce_csrf(request)
        id = verify_access_token(token)
        check_user(id)
        return self.get_user(validated_token), validated_token

        

class IsOwner(BasePermission):
    print('BasePermission')
    def has_object_permission(self, request, view, obj):
        print(obj, request)
        return obj.my_user == request.user