from rest_framework import routers

from contests.viewsets import ContestViewSet, ContestCategoryViewSet, ContestLevelViewSet

app_name = 'contests'

router = routers.DefaultRouter()
router.register('contests', ContestViewSet)
router.register('contests_cats', ContestCategoryViewSet)
router.register('contests_levels', ContestLevelViewSet)