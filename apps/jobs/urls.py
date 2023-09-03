from django.urls import include, path
from rest_framework import routers

from apps.jobs.views import CompanyViewSets, JobViewSets, UserViewSets

# app name for namespace
app_name = "jobs"

# create a router
router = routers.DefaultRouter()
router.register(r"jobs", JobViewSets)
router.register(r"user", UserViewSets)
router.register(r"company", CompanyViewSets)

urlpatterns = [path("", include(router.urls), name="Default")]
