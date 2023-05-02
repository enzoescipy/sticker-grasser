from rest_framework import serializers
from . import models 


#region USER
class User_all(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'password',
            'is_staff',
            'is_active',
            'is_superuser',
            'last_login',
            'date_joined'
        )
        model = models.User
        
class User_createSafe(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'password',
        )
        model = models.User

class User_readSafe(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'last_login',
            'date_joined'
        )
        model = models.User
#endregion


#region PROJECT

class Project_all(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'project_name',
            'todo_name'
        )
        model = models.Project

class Project_project(serializers.ModelSerializer):
    todo_name = ''
    class Meta:
        fields = (
            'user_id',
            'project_name',
        )
        model = models.Project

#endregion