from rest_framework import serializers
from . import models 
from django.db.models import Q
class BasicValidate():
    """
    convinent validation static functions.
    """

    harmful_strings =  ['*', '?', '%', '&', '$', '(', ')', '#', '^', '@', '!', '~', '+', '=', ",", "'", '"',"/", "."]
    harmful_email_strings =  ['*', '?', '%', '&', '$', '(', ')', '#', '^', '!', '~', '+', '=', ",", "'", '"',"/"]

    @classmethod
    def __is_harmless_str(cls, string:str, case:str = None) -> bool:
        """
        inspect the dangerous symbols included from string like :
        '*', '?', '%', '&', '$', '(', ')', '#', '^', '@', '!', '~', '+', '=', ",", "'", '"',"/", "."
        
        if case == "email", '@', '.'  will be excluded.
        
        Params:
            - str string : inspect targeted string
        Returns:
            - bool isHarmless
                + true -> dangerous symbols not included
                + false -> dangerous symbols included
        """
        harmful_strings = cls.harmful_strings
        if case == "email":
            harmful_strings = cls.harmful_email_strings
            
        for symbol in harmful_strings:
            if symbol in string:
                return False
        return True
                
    @staticmethod
    def validateType(value_type, name:str, value):
        """
        validate if 
            - value is type (type check)
            - value is not None

        """
        if type(value) is not value_type:
            CustomExceptionRaise.NoneOrTypeInvalidError(name)

    
    @staticmethod
    def validateString(name:str, value:str, allow_empty=False, allow_danger_character=False, case:str=""):
        """
        validate if
            - check if value is string and not None
            - check if value is not the empty string.
              (do not check if allow_empty=True)
            - chekc if value is not containing danger character
              (do not check if allow_danger_character=True)
        
        """
        if type(value) is not str:
            CustomExceptionRaise.NoneOrTypeInvalidError(paramName=name)
        elif len(value) < 1 and not allow_empty:
            CustomExceptionRaise.EmptyStringError(paramName=name)
        elif  not BasicValidate.__is_harmless_str(string=value, case=case) and not allow_danger_character:
            print(not BasicValidate.__is_harmless_str(string=value, case=case) and not allow_danger_character,
                  BasicValidate.__is_harmless_str(string=value, case=case),
                  allow_danger_character)
            CustomExceptionRaise.HarmfulInputError(paramName=name)


class CustomExceptionRaise():
    """
    convinent custom exception raise functions.
    WARNING : this is not the custom error handler!
    """
    @staticmethod
    def NoneOrTypeInvalidError(paramName):
        """
        paramName cannot be null or blank.
        """
        raise serializers.ValidationError(detail={paramName : f'{paramName} cannot be null or blank'})
    
    @staticmethod
    def EmptyStringError(paramName):
        """
        paramName string cannot be empty string.
        """
        raise serializers.ValidationError(detail={paramName : f'{paramName} string cannot be empty string.'})

    @staticmethod
    def HarmfulInputError(paramName):
        """
        paramName have(has) the harmful character(s).
        """
        raise serializers.ValidationError(detail={paramName : f'{paramName} have(has) the harmful character(s).'})
    
    @staticmethod
    def UniqueRuleViolatedError(paramName, uniqueModel):
        """
        paramName violated the UNIQUE rule that the params within uniqueModel must be UNIQUE.
        """
        raise serializers.ValidationError(detail={paramName : f'{paramName} violated the UNIQUE rule that the params within {uniqueModel} must be UNIQUE.'})

    @staticmethod
    def NotFoundError(paramName, notFoundModel):
        """
        paramName not found within the notFoundModel.
        """
        raise serializers.ValidationError(detail={paramName : f"{paramName} not found within the {notFoundModel}."})
    

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

class Project_CREATE_project(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)

    class Meta:
        model = models.Project
        fields = ['email', 'user_fkey', 'project_name']
        extra_kwargs = {'user_fkey':{'read_only':True}}
        
    def to_internal_value(self, data):
        email = data.get('email')
        project_name = data.get('project_name')
        # basic validations
        BasicValidate.validateString(name='project_name', value=project_name)
        # BasicValidate.validateString(name='email', value=email)

        # check if selected email is corredponding the unique user pkey
        queryset = models.User.objects.filter(email=email)
        if not queryset.exists():
            CustomExceptionRaise.NotFoundError(paramName='email', notFoundModel="User")
        user_fkey = queryset[0]

        # # check if logined user is matching with the request
        # self.isLogginedUserMatch(requested_user_id=user_fkey)

        # check if project_name is NOT already defined in the range of selected User.
        queryset = models.Project.objects.filter(Q(project_name=project_name) & Q(user_fkey=user_fkey.pk))
        if queryset.exists():
            CustomExceptionRaise.UniqueRuleViolatedError(paramName='project_name', uniqueModel="Project")
        
        return {
            'user_fkey': user_fkey,
            'project_name': project_name
        }
    
class Project_CREATE_todo(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)
    project_name = serializers.CharField(write_only=True)

    class Meta:
        model = models.Todo
        fields = ['email', 'project_name','project_fkey', 'todo_name']
        extra_kwargs = {'project_fkey':{'read_only':True}}
        
    def to_internal_value(self, data):
        project_name = data.get('project_name')
        todo_name = data.get('todo_name')
        email = data.get('email')

        # basic validations
        BasicValidate.validateString(name='project_name', value=project_name)
        BasicValidate.validateString(name='todo_name', value=todo_name)

        # check if selected email is corredponding the unique user pkey
        queryset = models.User.objects.filter(email=email)
        if not queryset.exists():
            CustomExceptionRaise.NotFoundError(paramName='email', notFoundModel="User")
        user_fkey = queryset[0]

        # check if selected project_name is corredponding the unique user pkey
        queryset = models.Project.objects.filter(project_name=project_name, user_fkey=user_fkey.pk)
        if not queryset.exists():
            CustomExceptionRaise.NotFoundError(paramName='project_name', notFoundModel="Project")
        project_fkey = queryset[0]

        # # check if logined user is matching with the request
        # self.isLogginedUserMatch(requested_user_id=project_fkey)

        # check if todo_name is NOT already defined in the range of selected Project.
        queryset = models.Todo.objects.filter(Q(todo_name=todo_name) & Q(project_fkey=project_fkey.pk))
        if queryset.exists():
            CustomExceptionRaise.UniqueRuleViolatedError(paramName='todo_name', uniqueModel="Project")
        
        return {
            'project_fkey': project_fkey,
            'todo_name': todo_name
        }



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