from rest_framework import serializers
from .models import CustomUser, Country, State, City

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

    def save(self, **kwargs):
        return super().save(**kwargs)

class StateSerializer(serializers.ModelSerializer):
    my_country__name = serializers.SerializerMethodField()
    my_country__my_user__name = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = '__all__'

    def get_my_country__name(self, obj):
        return obj.my_country.name if obj.my_country else None
    
    def get_my_country__my_user__name(self, obj):
        return obj.my_country.my_user.name if obj.my_country and obj.my_country.my_user else None

class CitySerializer(serializers.ModelSerializer):
    my_state__name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = '__all__'

    def get_my_state__name(self, obj):
        return obj.my_state.name if obj.my_state else None