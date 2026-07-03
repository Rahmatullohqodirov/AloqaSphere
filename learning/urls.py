from rest_framework.routers import DefaultRouter

from .views import LearningSessionViewSet, UserSubjectProgressViewSet

router = DefaultRouter()
router.register("sessions", LearningSessionViewSet, basename="session")
router.register("progress", UserSubjectProgressViewSet, basename="progress")

urlpatterns = router.urls
