from rest_framework import serializers
from .models import CustomUser, Country, State, City

class CitySerializer(serializers.ModelSerializer):
    # state = StateSerializer(many=True, read_only=True)
    # my_state__name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ("id",
            "name",
            "city_code",
            "phone_code",
            "population",
            "avg_age",
            "num_of_adult_males",
            "num_of_adult_females")

    # def get_my_state__name(self, obj):
    #     return obj.state.name if obj.state else None


class StateSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=True, read_only=True)
    # country_lists = CountrySerializer(many=True, read_only=True)
    # country = serializers.SerializerMethodField()
    # user = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = ('id', 'name', 'state_code', 'gst_code', 'city')

    # def get_country(self, obj):
    #     return {
    #         'name': obj.country.name,
    #         'country_code': obj.country.country_code,
    #         'phone_code': obj.country.phone_code,
    #         'currency_symbol': obj.country.curr_symbol
    #         } if obj.country else None
    
    # def get_user(self, obj):
    #     return {'username': obj.country.my_user.username, 'email': obj.country.my_user.email} if obj.country and obj.country.my_user else None

class CountrySerializer(serializers.ModelSerializer):
    state = StateSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ('name', 'country_code', 'curr_symbol', 'phone_code', 'state')

    def save(self, **kwargs):
        return super().save(**kwargs)
    
    
class UserSerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'country')