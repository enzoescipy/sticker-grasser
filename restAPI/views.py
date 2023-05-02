#backend/post/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins
from rest_framework import permissions as secure
from rest_framework.views import exceptions
from rest_framework.response import Response
from django.db.models import Q

from copy import deepcopy

from . import models
from . import serializers

"""
security level : 
    rwdc0 -> nobody can [read/write/delete/create] these value, debug checking only.
    rwdc1 -> only superuser can [read/write/delete/create] these value.
    rwdc2 -> only the authorized user can [read/write/delete/create] these value
        - rwdc range will be bounded in CURRENT user only. so, one cannot rwdc the other's data.
    rwdc3 -> all the un-authorized users can [read/write/delete/create] these value. 
"""

#region USER API

class User_RETRIEVE(generics.RetrieveAPIView):
    """
    # User_RETRIEVE
        SECURITY LEVEL r3 
        - get the specific user's information.
        - key param is <id> 
    GET params
        - id (char) : User model's id row.
    """
    serializer_class = serializers.User_readSafe
    permission_classes = []
    lookup_field = 'username'

    def get_queryset(self):
        return models.User.objects.filter(username = self.kwargs['username'])

class User_CREATE_unauthorized(generics.CreateAPIView):
    """
    # User_CREATE
        SECURITY LEVEL c2
        - create an user
        - staff, superuser will be always false
    POST params
        - Username
        - Email
        - password
    database changes
        - model User will get the new row of user
        - user will create without staff, superuser
    """
    serializer_class = serializers.User_createSafe
    permission_classes = []

#endregion

#region PROJECT API

class Project_CREATE_project(generics.CreateAPIView):
    """
    # Project_CREATE_project
        SECURITY LEVEL c2
        - create an project.
    POST params
        - user_id : specific user's id. 
        - project_name : project_name that will be created
    database changes
        - model Project will get new row of project.
        - row will created with todo_name='' (blank)
    """
    serializer_class = serializers.Project_project
    permission_classes = []

class Project_CREATE_todo(generics.CreateAPIView):
    """
    # Project_CREATE_todo
        SECURITY LEVEL c2
        - create an todo
        - if named project_name is not already exist in db, reject request. 
        - if project_name with that user already has the todo_name, reject request.
    POST params
        - user_id : specific user's id. 
        - project_name : project_name that will be created
        - todo_name : todo_name that will be created
    database changes
        - model Project will get new row of project.
        - row will created with todo_name=<todo_name>
    """

    serializer_class = serializers.Project_all
    permission_classes = []

    def query_validation(self):
        queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')
        if self.request.POST.get('todo_name') == '' or self.request.POST.get('todo_name') == None:
            raise exceptions.ValidationError('todo_name cannot be null or blank')
        
        queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id'))
                                                 & Q(todo_name = self.request.POST.get('todo_name')))
        if queryset.exists() == True:
            raise exceptions.ValidationError('todo_name must be unique if project_name and user_id is same.')
    
    def get_queryset(self):
        return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                            & Q(user_id = self.request.POST.get('user_id'))
                                            & Q(todo_name = self.request.POST.get('todo_name')))

    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)

class Project_RETRIEVE_project(mixins.ListModelMixin, generics.GenericAPIView):
    """
    # Project_RETRIEVE_project
        SECURITY LEVEL r2
        - retrieve the list of todo, inside of specific project.
        - only search for target project_name
    POST params
        - user_id
        - project_name
    """

    serializer_class = serializers.Project_project
    permission_classes = []

    def get_serializer_class(self):
        if len(self.request.POST) == 0:
            return serializers.Project_project
        else:
            return serializers.Project_all
        
    def query_validation(self):
        if len(self.request.POST) == 0:
            return models.Project.objects.none()
        
        queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))

        if queryset.exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with correct user_id.') 

    def get_queryset(self):
        return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                             & Q(user_id = self.request.POST.get('user_id')) 
                                             & ~Q(todo_name=''))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        return self.list(request, *args, **kwargs)

class Project_RETRIEVE_user(generics.ListAPIView):
    """
    # Project_RETRIEVE_user
        SECURITY LEVEL r2
        - retrieve the list of project, with the specific user.
        - only search for target user_id
    GET params
        - user_id
    """

    serializer_class = serializers.Project_project
    permission_classes = []
    lookup_field = 'user_id'

    def get_queryset(self):
        return models.Project.objects.filter(user_id = self.kwargs['user_id'])



class Project_DELETE_todo(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Project_DELETE_todo
        SECURITY LEVEL d2
        - delete the todo in a project.
        - only search for target project_name
    POST params
        - user_id
        - project_name
        - todo_name
    database changes
        - targeted todo will be deleted.
    """

    serializer_class = serializers.Project_all
    permission_classes = []

    def query_validation(self):
        queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')
        if self.request.POST.get('todo_name') == '' or self.request.POST.get('todo_name') == None:
            raise exceptions.ValidationError('target todo_name cannot be null or blank')

    def get_queryset(self):
        return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id'))
                                                 & Q(todo_name = self.request.POST.get('todo_name')))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response
    
class Project_DELETE_project(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Project_DELETE_project
        SECURITY LEVEL d2
        - delete the rows whose have the same project_name in the model.
        - only search for target project_name.
    POST params
        - user_id
        - project_name
    database changes
        - all of todo s with has same project_name will be deleted.
    """

    serializer_class = serializers.Project_project
    permission_classes = []

    def query_validation(self):
        if self.get_queryset().exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')

    def get_queryset(self):
        return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
         

    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response


#endregion