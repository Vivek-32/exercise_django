from rest_framework import serializers
from .models import CustomUser, Country, State, City

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    # user = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = '__all__'

    def save(self, **kwargs):
        return super().save(**kwargs)
    

class StateSerializer(serializers.ModelSerializer):
    # country_lists = CountrySerializer(many=True, read_only=True)
    country = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = '__all__'

    def get_country(self, obj):
        return {
            'name': obj.country.name,
            'country_code': obj.country.country_code,
            'phone_code': obj.country.phone_code,
            'currency_symbol': obj.country.curr_symbol
            } if obj.country else None
    
    def get_user(self, obj):
        return {'username': obj.country.my_user.username, 'email': obj.country.my_user.email} if obj.country and obj.country.my_user else None

class CitySerializer(serializers.ModelSerializer):
    # state = StateSerializer(many=True, read_only=True)
    my_state__name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = '__all__'

    def get_my_state__name(self, obj):
        return obj.state.name if obj.state else None