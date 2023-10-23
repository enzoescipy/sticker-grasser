from rest_framework import serializers
from . import models 


user_fkey_str = 'user_fkey'


#region USER
class User_createSafe(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'password',
        )
        model = models.User
    
    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

class User_updateSafe(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email',
            'password',
        )
        model = models.User
    
    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.set_password(validated_data["password"])
        instance.save()

        return instance

class User_emailMixin(serializers.ModelSerializer):
    class Meta:
        fields = (
            'email',
        )
        model = models.User

#endregion


#region PROJECT

class Project(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_fkey',
            'project_name',
        )
        model = models.Project


# class Project_set(serializers.Serializer):
#     # user_fkey = serializers.PrimaryKeyRelatedField(queryset = models.User.objects.all)
#     email = serializers.CharField(max_length=models.field_length_dict['email'])
#     project_name = serializers.CharField(max_length=models.field_length_dict['name'])

# class Project_user(serializers.ModelSerializer):
#     project_name = ''
#     class Meta:
#         fields = (
#             'user_fkey',
#         )
#         model = models.Project

class Todo_get(serializers.ModelSerializer):
    class Meta:
        fields = (
            'project_fkey',
            'todo_name',
        )
        model = models.Todo


#endregion

#region  STAMP

class Stamp(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_fkey',
            'stamp_name',
        )
        model = models.Stamp

class DefFunc(serializers.ModelSerializer):
    class Meta:
        fields = (
            'stamp_fkey',
            'defFunc_name',
        )
        model = models.DefFunc

class FuncArg(serializers.ModelSerializer):
    class Meta:
        fields = (
            'stamp_fkey',
            'arg_name',
            'arg_value',
        )
        model = models.FuncArg


# class Stamp_subelement_argsGet(serializers.Serializer):
#     user_id = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.all()) 

#     stamp_name = serializers.CharField()
#     subelement_name = serializers.CharField()
#     defFunc_name = serializers.CharField()

#     arg_names = serializers.CharField()
#     arg_vals = serializers.CharField()

# 

#endregion


# region MAIN

class UserTodoStampOwnedHistory(serializers.ModelSerializer):
    class Meta:
        fields = (
            'user_fkey',
            'stamp_fkey',
            'todo_fkey',
            'history_fkey',
        )
        model = models.UserTodoStampOwnedHistory

class History(serializers.ModelSerializer):
    class Meta:
        fields = (
            'date',
        )
        model = models.History

class HistoryArg(serializers.ModelSerializer):
    class Meta:
        fields = (
            'history_fkey',
            'arg_name',
            'arg_value',
        )
        model = models.HistoryArg


# endregion