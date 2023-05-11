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

from . import subelement as sub


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
        # project_name, user_id check
        queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')
        # todo_name null check.
        # if null validation not done, it can delete THE WHOLE PROJECT Ref.
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

#region STAMP API

class Stamp_CREATE_stamp(generics.CreateAPIView):
    """
    # Stamp_CREATE_stamp
        SECURITY LEVEL c2
        - create an stamp.
    POST params
        - user_id : specific user's id. 
        - stamp_name : stamp_name that will be created
    database changes
        - model Stamp will get new row of stamp.
        - row will created with user_id, stamp_name and other parms = (blank)
    """   


    serializer_class = serializers.Stamp_stamp
    permission_classes = []

    def query_validation(self):

        if self.get_queryset().exists() == True:
            raise exceptions.ValidationError('cannot add stamp that already has been exist.')
        
    def get_queryset(self):
        queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_name = self.request.POST.get('stamp_name')))
        return queryset
        
    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)
    
class Stamp_CREATE_subelement(generics.CreateAPIView):
    """
    # Stamp_CREATE_subelement
        SECURITY LEVEL c2
        - create an subelement on the existing stamp
        - if named stamp_name is not already exist in db, reject request. 
    POST params
        - user_id : specific user's id. 
        - stamp_name : stamp_name already exists.
        - subelement_name : subelement_name that will be created
        - defFunc_name : defFunc_name that will be created
    database changes
        - model Stamp will get new row of Stamp.
        - row will created with subelement_name=<subelement_name>, defFunc_name=<defFunc_name>
    """

    serializer_class = serializers.Stamp_subelement
    permission_classes = []

    def query_validation(self):
        queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_name = self.request.POST.get('stamp_name')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
        if self.request.POST.get('subelement_name') == '' or self.request.POST.get('subelement_name') == None or self.request.POST.get('defFunc_name') == '' or self.request.POST.get('defFunc_name') == None:
            raise exceptions.ValidationError('subelement_name and defFunc_name cannot be null or blank')
    
    def get_queryset(self):
        return models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
                                            & Q(stamp_name = self.request.POST.get('stamp_name'))
                                            & Q(subelement_name = self.request.POST.get('subelement_name'))
                                            & Q(defFunc_name = self.request.POST.get('defFunc_name')))

    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)

class Stamp_CREATE_arg(generics.CreateAPIView):
    """
    # Stamp_CREATE_subelement
        SECURITY LEVEL c2
        - create an subelement on the existing subelement
        - if named subelement is not already exist in stamp, reject request. 
    POST params
        - user_id : specific user's id. 
        - stamp_name : stamp_name already exists.
        - subelement_name : subelement_name that already be exists
        - arg_name : element's key part.
        - arg_val : element's value part.
    database changes
        - model Stamp will get new row of Stamp.
        - row will created with subelement_name=<subelement_name>, defFunc_name='', also argname&val&type respectively.
    """

    serializer_class = serializers.Stamp_subelement
    permission_classes = []

    def query_validation(self):
        queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_name = self.request.POST.get('stamp_name'))
                                                 & Q(subelement_name = self.request.POST.get('subelement_name')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
        
        if (self.request.POST.get('arg_name') == '' or self.request.POST.get('arg_name') == None 
            or self.request.POST.get('arg_val') == '' or self.request.POST.get('arg_val') == None 
            or self.request.POST.get('arg_val') == '' or self.request.POST.get('arg_val') == None):
            raise exceptions.ValidationError('arg_name, arg_val cannot be null or blank')
    
        queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_name = self.request.POST.get('stamp_name'))
                                                 & Q(subelement_name = self.request.POST.get('subelement_name'))
                                                 & Q(arg_name = self.request.POST.get('arg_name')))
        if queryset.exists() == True:
            raise exceptions.ValidationError('arg_name must NOT already exists in the db.')
    def get_queryset(self):
        return models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
                                            & Q(stamp_name = self.request.POST.get('stamp_name'))
                                            & Q(subelement_name = self.request.POST.get('subelement_name'))
                                            & Q(defFunc_name = self.request.POST.get('defFunc_name'))
                                            & Q(arg_name = self.request.POST.get('arg_name'))
                                            & Q(arg_val = self.request.POST.get('arg_val')))

    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)

class Stamp_RETRIEVE_user(generics.ListAPIView):
    """
    # Project_RETRIEVE_user
        SECURITY LEVEL r2
        - retrieve the list of stamp, with the specific user.
        - only search for target user_id
    GET params
        - user_id
    """

    permission_classes = []
    lookup_field = 'user_id'
    serializer_class = serializers.Stamp_stamp

    def get_queryset(self):
        return models.Stamp.objects.filter(user_id = self.kwargs['user_id'])

class Stamp_RETRIEVE_stamp(mixins.ListModelMixin, generics.GenericAPIView):
    """
    # Project_RETRIEVE_project
        SECURITY LEVEL r2
        - retrieve the list of subelement, inside of specific project.
        - only search for target project_name
    POST params
        - user_id
        - stamp_name
    """

    permission_classes = []

    def get_serializer_class(self):
        if len(self.request.POST) == 0:
            return serializers.Stamp_stamp
        else:
            return serializers.Stamp_subelement
        
    def query_validation(self):
        if len(self.request.POST) == 0:
            return models.Stamp.objects.none()
        
        queryset = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))

        if queryset.exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with correct user_id.') 

    def get_queryset(self):
        return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                             & Q(user_id = self.request.POST.get('user_id')) 
                                             & ~Q(subelement_name='') & Q(arg_name = ''))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        return self.list(request, *args, **kwargs)

class Stamp_RETRIEVE_subelement(generics.ListAPIView):
    """
    # Stamp_RETRIEVE_subelement
        SECURITY LEVEL r2
        - retrieve the list of args, with the specific subelement.
        -  search for target stamp.
    GET params
        - user_id
        - stamp_name
        - subelement_name
    """

    serializer_class = serializers.Stamp_subelement_retrieve
    permission_classes = []

    def get_serializer_class(self):
        if len(self.request.POST) == 0:
            return serializers.Stamp_subelement_retrieve
        else:
            return serializers.Stamp_all
        
    def query_validation(self):
        if len(self.request.POST) == 0:
            return models.Stamp.objects.none()
        
        queryset = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(subelement_name = self.request.POST.get('subelement_name'))
                                                 & Q(user_id = self.request.POST.get('user_id')))

        if queryset.exists() == False:
            raise exceptions.ValidationError('stamp_name and subelement_name must already exists in the db with correct user_id.') 

    def get_queryset(self):
        return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                             & Q(subelement_name = self.request.POST.get('subelement_name'))
                                             & Q(user_id = self.request.POST.get('user_id')) 
                                             & ~Q(arg_name=''))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        return self.list(request, *args, **kwargs)

class Stamp_DELETE_stamp(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Stamp_DELETE_stamp
        SECURITY LEVEL d2
        - delete the stamp in a project.
        - only search for target stamp_name
    POST params
        - user_id
        - stamp_name
        - todo_name
    database changes
        - targeted stamp will be deleted.
    """

    serializer_class = serializers.Stamp_stamp
    permission_classes = []

    def query_validation(self):
        if self.get_queryset().exists() == False:
            raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')

    def get_queryset(self):
        return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response
    
class Stamp_DELETE_subelement(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Stamp_DELETE_subelement
        SECURITY LEVEL d2
        - delete the subelement in a project_name.
    POST params
        - user_id
        - project_name
        - todo_name
        - subelement_name
    database changes
        - targeted subelement will be deleted.
    """

    serializer_class = serializers.Stamp_subelement_retrieve
    permission_classes = []

    def query_validation(self):
        # validate existance of stamp_name, user_id
        query = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id')))
        if query.exists() == False:
            raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
        # null check for subelement_name
        if self.request.POST.get('subelement_name') == '' or self.request.POST.get('subelement_name') == None:
            raise exceptions.ValidationError('target subelement_name cannot be null or blank')

    def get_queryset(self):
        return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id'))
                                                 & Q(subelement_name = self.request.POST.get('subelement_name')))
    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response

class Stamp_DELETE_arg(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Stamp_DELETE_arg
        SECURITY LEVEL d2
        - delete the arg in a project_name.
    POST params
        - user_id
        - project_name
        - todo_name
        - arg_name
    database changes
        - targeted arg will be deleted.
    """

    serializer_class = serializers.Stamp_arg
    permission_classes = []

    def query_validation(self):
        # validate existance of stamp_name, user_id, arg_name
        if self.get_queryset().exists() == False:
            raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
        # null check for arg_name
        if self.request.POST.get('arg_name') == '' or self.request.POST.get('arg_name') == None:
            raise exceptions.ValidationError('target arg_name cannot be null or blank')

    def get_queryset(self):
        return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
                                                 & Q(user_id = self.request.POST.get('user_id'))
                                                 & Q(arg_name = self.request.POST.get('arg_name')))
    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response
    
#endregion


#region MAIN_API

class Main_CREATE_main(generics.CreateAPIView):
    """
    # Main_CREATE_main
        SECURITY LEVEL c2
        - create an main recode.
        - you CAN create the two identical recode in db. they will be count as 2 stamps in the same day
    POST params
        - user_id : specific user's id. 
        - stamp_id : specific stamp_id.
        - date : date hope to put in the recode
    database changes
        - model Main will get new row of recode.
        - without arg.
    """   

    serializer_class = serializers.Main_main
    permission_classes = []


    def query_validation(self):
        # validation of existance
        if self.get_queryset().exists() == True:
            raise exceptions.ValidationError('cannot add recode that already has been exist.')
        
        # validation of foregin key relation matching
        self.serializer_class = serializers.Stamp_all
        stamp_user = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
                                                & Q(id = self.request.POST.get('stamp_id')))
        if stamp_user.exists() == False:
            raise exceptions.ValidationError('targeted user must already have the targeted stamp.')
        self.serializer_class = serializers.Main_main
        
    def get_queryset(self):
        queryset = models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_id = self.request.POST.get('stamp_id'))
                                                 & Q(date = self.request.POST.get('date')))
        return queryset
        
    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)
    
class Main_CREATE_arg(generics.CreateAPIView):
    """
    # Main_CREATE_main
        SECURITY LEVEL c2
        - create an subvals to main recode.

    POST params
        - user_id : target user's id. 
        - stamp_id : target stamp_id.

    database changes
        - model Main will get new row of recode.
        - without arg.
    """   

    serializer_class = serializers.Main_all
    permission_classes = []


    def query_validation(self):
        # validation of existance
        queryset = models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_id = self.request.POST.get('stamp_id'))
                                                 & Q(date = self.request.POST.get('date')))
        if queryset.exists() == False:
            raise exceptions.ValidationError('can add arg only if user+stamp already has been exist.')

    def get_queryset(self):
        queryset = models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_id = self.request.POST.get('stamp_id'))
                                                 & Q(date = self.request.POST.get('date')))
        return queryset
        
    def create(self, request, *args, **kwargs):
        self.query_validation()
        return super().create(request, *args, **kwargs)
    
class Main_DELETE_main(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Main_DELETE_main
        SECURITY LEVEL d2
        - delete the recode in a db.
        - only search for target stamp + date
    POST params
        - user_id
        - stamp_id
        - date
    database changes
        - targeted recode will be deleted.
    """

    serializer_class = serializers.Main_main
    permission_classes = []

    def query_validation(self):
        # project_name, user_id check
        if self.get_queryset().exists() == False:
            raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')

    def get_queryset(self):
        return models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_id = self.request.POST.get('stamp_id'))
                                                 & Q(date = self.request.POST.get('date')))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.get_queryset().delete()
        return response

class Main_DELETE_arg(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    # Main_DELETE_arg
        SECURITY LEVEL d2
        - delete the specific arg in a db.
        - only search for target stamp + date
    POST params
        - user_id
        - stamp_id
        - date
        - arg_name
    database changes
        - targeted arg will be deleted.
    """

    serializer_class = serializers.Main_arg
    permission_classes = []

    def query_validation(self):
        # project_name, user_id check
        if self.get_queryset().exists() == False:
            raise exceptions.ValidationError('stamp+user must already exists in the db.')
        # arg null check.
        if self.request.POST.get('arg_name') == '' or self.request.POST.get('arg_name') == None:
            raise exceptions.ValidationError('target arg_name cannot be null or blank')

    def get_queryset(self):
        return models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
                                                 & Q(stamp_id = self.request.POST.get('stamp_id'))
                                                 & Q(date = self.request.POST.get('date'))
                                                 & Q(arg_name = self.request.POST.get('arg_name')))

    def post(self, request, *args, **kwargs):
        self.query_validation()
        response = self.list(request, *args, **kwargs)
        self.serializer_class = serializers.Main_all
        self.get_queryset().delete()
        return response


#endregion
