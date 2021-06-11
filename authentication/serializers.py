from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        #cheks if email is unique and raises error if not
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        required=True,
        #cheks if username is unique and raises error if not
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)
    company_name = serializers.CharField(max_length=150, 
        required=False,
        #cheks if company_name is unique and raises error if not
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['email','username','first_name','last_name',
                'password', 'company_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
