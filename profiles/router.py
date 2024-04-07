from rest_framework import routers

from profiles.viewsets import ProfileViewSet

app_name = 'profiles'

router = routers.DefaultRouter()
router.register('', ProfileViewSet)
