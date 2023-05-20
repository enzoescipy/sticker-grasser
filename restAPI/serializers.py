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

#region  STAMP

class Stamp_all(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'stamp_name',
            'subelement_name',
            'defFunc_name',
            'arg_name',
            'arg_val',
        )
        model = models.Stamp

class Stamp_arg(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'stamp_name',
            'subelement_name',
            'arg_name',
        )
        model = models.Stamp

class Stamp_subelement_argsGet(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all()) 

    stamp_name = serializers.CharField()
    subelement_name = serializers.CharField()
    defFunc_name = serializers.CharField()

    arg_names = serializers.CharField()
    arg_vals = serializers.CharField()

class Stamp_subelement(serializers.ModelSerializer):
    class Meta:
        arg_name = ''
        arg_val = ''
        fields = (
            'user_id',
            'stamp_name',
            'subelement_name',
            'defFunc_name',
        )
        model = models.Stamp

class Stamp_subelement_retrieve(serializers.ModelSerializer):
    class Meta:
        arg_name = ''
        arg_val = ''
        fields = (
            'user_id',
            'stamp_name',
            'subelement_name',

        )
        model = models.Stamp

class Stamp_stamp(serializers.ModelSerializer):
    class Meta:
        arg_name = ''
        arg_val = ''
        subelement_name = ''
        defFunc_name = ''
        fields = (
            'user_id',
            'stamp_name',
        )
        model = models.Stamp


#endregion


# region MAIN

class Main_all(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'stamp_id',
            'date',
            'arg_name',
            'arg_val',
        )
        model = models.Main

class Main_main(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'stamp_id',
            'date',
        )
        model = models.Main

class Main_arg(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_id',
            'stamp_id',
            'date',
            'arg_name',
        )
        model = models.Main

# endregion