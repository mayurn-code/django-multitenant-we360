from rest_framework import serializers
from .models import Client,SignUp

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["domain_url", "schema_name", "name","subdomain","basedomain","clientid","signupuserid"]



class SignupSerializer(serializers.ModelSerializer):

    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zipcode = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = SignUp
        fields = ["email", "username", "firstname","lastname","company_name","address","city","state","country","zipcode"]
    
    