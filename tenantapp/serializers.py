from rest_framework import serializers
from .models import Hotels


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotels
        fields = ["hotel_name"]