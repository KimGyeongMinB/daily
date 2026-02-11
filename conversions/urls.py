from django.urls import path

from .views import ConversionAPIView

app_name = "conversions"

urlpatterns = [
    path('transform/', ConversionAPIView.as_view(), name="transform"),
    path("transform/<int:conversion_id>/", ConversionAPIView.as_view()),
]