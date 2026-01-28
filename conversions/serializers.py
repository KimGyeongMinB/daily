from rest_framework import serializers
from .models import Conversion

class ConversionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversion
        fields = ("id", "text", "url", "result", "status", "created_at")
        read_only_fields = ("id", "author", "result", "status", "created_at")

    def validate(self, attrs):
        text = attrs.get("text")
        url = attrs.get("url")

        if not text and not url:
            raise serializers.ValidationError("text 또는 url 중 하나는 필수입니다.")
        
        if text and url:
            attrs["url"] = None

        if text:
            attrs["text"] = text

        return attrs