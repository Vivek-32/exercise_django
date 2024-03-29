from django.urls import path
from exercise_app import views

urlpatterns = [
    # path('bulk-insert/', view=views.bulk_insert, name='bulk-insert'),
    # path('bulk-update/', view=views.bulk_update, name='bulk-update'),
    # path('fetch-all/', view=views.fetch_all, name='fetch-all'),
    # path('fetch-all-cities-specific-state/', view=views.fetch_all_cities_specific_state, name='fetch-all-cities-specific-state'),
    # path('fetch-all-state-specific-country/', view=views.fetch_all_state_specific_country, name='fetch-all-state-specific-country'),
    # path('fetch-all-cities-specific-country/', view=views.fetch_all_cities_specific_Country, name='fetch-all-cities-specific-country'),
    # path('fetch-max-min-population/', view=views.fetch_max_min_population, name='fetch-max-min-population'),
    path('users/', view=views.UserListAPIView.as_view(), name="user-list"),
    path('users/<int:pk>/', view=views.UserDetailAPIView.as_view(), name='user-detail'), 
    path('sign-in/', view=views.SignInAPIView.as_view(), name='sign-in'),
    path('sign-out/', view=views.SignoutAPIView.as_view(), name='sign-out'),
    path('country/', view=views.CountryCreateListView.as_view(), name='country-create-list'),
    path('country/<str:pk>/', view=views.CountryDetailAPIView.as_view(), name='country-retrieve-update-delete'),
    path('state/', view=views.StateCreateListView.as_view(), name='state-create-list'),
    path('state/<str:pk>/', view=views.StateDetailAPIView.as_view(), name='state-retrieve-update-delete'),
    path('city/', view=views.CityListCreateView.as_view(), name='state-create-list'),
    path('city/<str:pk>/', view=views.CityDetailView.as_view(), name='city-retrieve-update-delete'),
]