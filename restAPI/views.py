#backend/post/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model  
from rest_framework import generics, mixins, status
from rest_framework import permissions 
from rest_framework.views import exceptions
from rest_framework.response import Response
from django.db.models import Q

# from copy import deepcopy

from . import models
from . import serializers

from . import subelement as sub

"""
security level : 
    CRUD0 -> nobody can [read/write/delete/create] these value, superuser only.
    CRUD1 -> only staff can [read/write/delete/create] these value.
    CRUD2 -> only the authorized user can access this view, only for named by matching user.
        - one cannot CRUD the other user's data. that means requested user_id could be mached to loggined user_id.
        - staff can access CRUD of this data.
    CRUD3 -> only the authorized user can [read/write/delete/create] these value freely.
    CRUD4 -> all the un-authorized users can [read/write/delete/create] these value. 
"""
user_fkey_str = serializers.user_fkey_str
# WARNING : you must get the current target user pkey, and call it like self.isLogginedUserMatch(user_pk) !
# you should override the get_queryset method and execute the query_validation manually.
# class bject):
#     def isLogginedUserMatch(self, requested_user):
#         # check if owner of instance is matched the caller of this view.
#         logged_in_user = self.request.user

#         print("ecurity validation : ", requested_user, logged_in_user)
        
#         if logged_in_user != requested_user:
#             superuser = getattr(logged_in_user, "is_superuser")
#             if superuser != True:
#                 # return False
#                 raise exceptions.ValidationError("current logged in user have not owned licence for this request.")
#         # return True



#region USER API

class User_CREATE(generics.CreateAPIView):
    """
    # User_CREATE
        SECURITY LEVEL C4
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({}, status=status.HTTP_200_OK, headers=headers)

class User_UPDATE(generics.UpdateAPIView):
    """
    # User_UPDATE
        SECURITY LEVEL U2
        - update an user profile
        - targeted user is currently logged in user.
    POST params
        - password
    database changes
        - logged in user will be updated.
    """
    serializer_class = serializers.User_updateSafe
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_200_OK)

"""
User_DELETE : D0, unsupported.
"""


#endregion

## region PROJECT API

class Project_CREATE_project(generics.CreateAPIView):
    """
    # Project_CREATE_project
        SECURITY LEVEL C2
        - create an project model row.
    POST params
        - project_name : project_name (UNIQUE by each User)
            -> project_name that will be created
    database changes
        - model Project will get the new row of project.
    """
    serializer_class = serializers.Project_CREATE_project
    queryset = models.Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.inject_user(self.request.user)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class Project_CREATE_todo(generics.CreateAPIView):
    """
    # Project_CREATE_todo
        SECURITY LEVEL C2
        - create an todo model row.
    POST params
        - project_name : project_name that will be created
        - todo_name : todo_name that will be created
    database changes
        - model Project will get new row of project.
        - row will created with todo_name=<todo_name>
    """

    serializer_class = serializers.Project_CREATE_todo
    queryset = models.Todo.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.inject_user(self.request.user)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

class Project_RETRIEVE_project(generics.ListAPIView):
    """
    # Project_RETRIEVE_project
        SECURITY LEVEL r2
        - retrieve the list of todo, inside of specific project.
        - only search for target project_name
    POST params
        - email
        - project_name
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.Project_RETRIEVE_project

    def get_queryset(self):
        return models.Project.objects.filter(user_fkey=self.request.user)        
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.list(serializer.data, status=status.HTTP_200_OK)

# class Project_RETRIEVE_user(mixins.ListModelMixin, generics.GenericAPIView, 
#     """
#     # Project_RETRIEVE_user
#         SECURITY LEVEL r2
#         - retrieve the list of project, with the specific user.
#         - only search for target user_id
#     GET params
#         - user_id
#     """

#     serializer_class = serializers.Project_user
#     permission_classes = [permissions.IsAuthenticated]

#     def get_serializer_class(self):
#         if len(self.request.POST) == 0:
#             return serializers.Project_user
#         else:
#             return serializers.Project_project
        
#     def get_queryset(self):
#         self.query_validation()
#         return models.Project.objects.filter(user_id = self.request.POST.get("user_id"))
    
#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         return self.list(request, *args, **kwargs)
    
# class Project_DELETE_todo(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, 
#     """
#     # Project_DELETE_todo
#         SECURITY LEVEL d2
#         - delete the todo in a project.
#         - only search for target project_name
#     POST params
#         - user_id
#         - project_name
#         - todo_name
#     database changes
#         - targeted todo will be deleted.
#     """

#     serializer_class = serializers.Project_all
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         # project_name, user_id check
#         queryset = models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id')))
#         if queryset.exists() == False:
#             raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')
#         # todo_name null check.
#         # if null validation not done, it can delete THE WHOLE PROJECT Ref.
#         if self.request.POST.get('todo_name') == '' or self.request.POST.get('todo_name') == None:
#             raise exceptions.ValidationError('target todo_name cannot be null or blank')

#     def get_queryset(self):
#         return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id'))
#                                                  & Q(todo_name = self.request.POST.get('todo_name')))

#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         response = self.list(request, *args, **kwargs)
#         self.get_queryset().delete()
#         return response
    
# class Project_DELETE_project(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, 
#     """
#     # Project_DELETE_project
#         SECURITY LEVEL d2
#         - delete the rows whose have the same project_name in the model.
#         - only search for target project_name.
#     POST params
#         - user_id
#         - project_name
#     database changes
#         - all of todo s with has same project_name will be deleted.
#     """

#     serializer_class = serializers.Project_project
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         if self.get_queryset().exists() == False:
#             raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')

#     def get_queryset(self):
#         return models.Project.objects.filter(Q(project_name=self.request.POST.get('project_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id')))
         

#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         response = self.list(request, *args, **kwargs)
#         self.get_queryset().delete()
#         return response


# #endregion

# #region STAMP API

# class Stamp_CREATE_stamp(generics.CreateAPIView, 
#     """
#     # Stamp_CREATE_stamp
#         SECURITY LEVEL c2
#         - create an stamp.
#     POST params
#         - user_id : specific user's id. 
#         - stamp_name : stamp_name that will be created
#     database changes
#         - model Stamp will get new row of stamp.
#         - row will created with user_id, stamp_name and other parms = (blank)
#     """   


#     serializer_class = serializers.Stamp_stamp
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         if self.get_queryset().exists() == True:
#             raise exceptions.ValidationError('cannot add stamp that already has been exist.')
        
#     def get_queryset(self):
#         queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
#                                                  & Q(stamp_name = self.request.POST.get('stamp_name')))
#         return queryset
        
#     def create(self, request, *args, **kwargs):
#         self.query_validation()
#         return super().create(request, *args, **kwargs)
    
# class Stamp_CREATE_subelement(generics.CreateAPIView, 
#     """
#     # Stamp_CREATE_subelement
#         SECURITY LEVEL c2
#         - create an subelement on the existing stamp
#         - if named stamp_name is not already exist in db, reject request. 
#     POST params
#         - user_id : specific user's id. 
#         - stamp_name : stamp_name already exists.
#         - subelement_name : subelement_name that will be created
#         - defFunc_name : defFunc_name that will be created
#         - arg_names -> args for defFunc
#         - arg_vals -> args for defFunc
#     database changes
#         - model Stamp will get new row of Stamp.
#         - row will created with subelement_name=<subelement_name>, defFunc_name=<defFunc_name>
#     """

#     serializer_class = serializers.Stamp_subelement_argsGet
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         queryset = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
#                                                  & Q(stamp_name = self.request.POST.get('stamp_name')))
#         if queryset.exists() == False:
#             raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
#         if self.request.POST.get('subelement_name') == '' or self.request.POST.get('subelement_name') == None or self.request.POST.get('defFunc_name') == '' or self.request.POST.get('defFunc_name') == None:
#             raise exceptions.ValidationError('subelement_name and defFunc_name cannot be null or blank')
    
#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
#                                             & Q(stamp_name = self.request.POST.get('stamp_name'))
#                                             & Q(subelement_name = self.request.POST.get('subelement_name'))
#                                             & Q(defFunc_name = self.request.POST.get('defFunc_name')))

#     def create(self, request, *args, **kwargs):
#         self.query_validation()

#         user_id = self.request.POST.get('user_id')
#         stamp_name = self.request.POST.get('stamp_name')
#         subelement_name = self.request.POST.get('subelement_name')
#         defFunc_name = self.request.POST.get('defFunc_name')


#         # arg_names, arg_vals split with blank
#         arg_names = self.request.POST.get("arg_names")
#         arg_vals = self.request.POST.get("arg_vals")
#         arg_names = arg_names.split(' ')
#         arg_vals = arg_vals.split(' ')

#         # args validation for len()
#         if len(arg_names) != len(arg_vals):
#             raise exceptions.ValidationError('arg_names and arg_vals must have the same length of elements as sep=\' \'.')

#         # make subelement set dict
#         set_dict = None
#         if defFunc_name == "discrete_point" :
#             args_dict = dict(zip(arg_names, arg_vals))
#             set_dict = sub.Discrete_point.subelement_set(**args_dict)
#         else :
#             raise exceptions.ValidationError('wrong name : defFunc_name ')


#         # create arg_rows in models.Stamp
#         for k,v in set_dict.items():
#             arg_name = k
#             arg_val = v
#             models.Stamp.objects.create(user_id=models.User.objects.get(id=int(user_id)), 
#                                         stamp_name=stamp_name, 
#                                         subelement_name=subelement_name,
#                                         defFunc_name = defFunc_name,
#                                         arg_name = arg_name,
#                                         arg_val = arg_val)

#         models.Stamp.objects.create(user_id=models.User.objects.get(id=int(user_id)), 
#                                         stamp_name=stamp_name, 
#                                         subelement_name=subelement_name,
#                                         defFunc_name = defFunc_name) # create subelement descriptional row

#         # make response then return
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

# class Stamp_RETRIEVE_user(mixins.ListModelMixin, generics.GenericAPIView, 
#     """
#     # Project_RETRIEVE_user
#         SECURITY LEVEL r2
#         - retrieve the list of stamp, with the specific user.
#         - only search for target user_id
#     GET params
#         - user_id
#     """

#     serializer_class = serializers.Stamp_user
#     permission_classes = [permissions.IsAuthenticated]

#     def get_serializer_class(self):
#         if len(self.request.POST) == 0:
#             return serializers.Stamp_user
#         else:
#             return serializers.Stamp_stamp
        
#     def get_queryset(self):
#         self.query_validation()
#         return models.Stamp.objects.filter(user_id = self.request.POST.get("user_id"))
    
#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         return self.list(request, *args, **kwargs)
    
# class Stamp_RETRIEVE_stamp(mixins.ListModelMixin, generics.GenericAPIView, 
#     """
#     # Project_RETRIEVE_project
#         SECURITY LEVEL r2
#         - retrieve the list of subelement, inside of specific project.
#         - only search for target project_name
#     POST params
#         - user_id
#         - stamp_name
#     """

#     permission_classes = [permissions.IsAuthenticated]

#     def get_serializer_class(self):
#         if len(self.request.POST) == 0:
#             return serializers.Stamp_stamp
#         else:
#             return serializers.Stamp_subelement
        
#     def query_validation(self):
#         super().query_validation()
#         if len(self.request.POST) == 0:
#             return models.Stamp.objects.none()
        
#         queryset = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id')))

#         if queryset.exists() == False:
#             raise exceptions.ValidationError('project_name must already exists in the db with correct user_id.') 

#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                              & Q(user_id = self.request.POST.get('user_id')) 
#                                              & ~Q(subelement_name='') & Q(arg_name = ''))

#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         return self.list(request, *args, **kwargs)

# class Stamp_RETRIEVE_subelement(generics.ListAPIView, 
#     """
#     # Stamp_RETRIEVE_subelement
#         SECURITY LEVEL r2
#         - retrieve the list of args, with the specific subelement.
#         -  search for target stamp.
#     GET params
#         - user_id
#         - stamp_name
#         - subelement_name
#     """

#     serializer_class = serializers.Stamp_subelement_retrieve
#     permission_classes = [permissions.IsAuthenticated]

#     def get_serializer_class(self):
#         if len(self.request.POST) == 0:
#             return serializers.Stamp_subelement_retrieve
#         else:
#             return serializers.Stamp_all
        
#     def query_validation(self):
#         super().query_validation()
#         if len(self.request.POST) == 0:
#             return models.Stamp.objects.none()
        
#         queryset = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                                  & Q(subelement_name = self.request.POST.get('subelement_name'))
#                                                  & Q(user_id = self.request.POST.get('user_id')))

#         if queryset.exists() == False:
#             raise exceptions.ValidationError('stamp_name and subelement_name must already exists in the db with correct user_id.') 

#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                              & Q(subelement_name = self.request.POST.get('subelement_name'))
#                                              & Q(user_id = self.request.POST.get('user_id')) 
#                                              & ~Q(arg_name=''))

#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         return self.list(request, *args, **kwargs)

# class Stamp_DELETE_stamp(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, 
#     """
#     # Stamp_DELETE_stamp
#         SECURITY LEVEL d2
#         - delete the stamp in a project.
#         - only search for target stamp_name
#     POST params
#         - user_id
#         - stamp_name
#         - todo_name
#     database changes
#         - targeted stamp will be deleted.
#     """

#     serializer_class = serializers.Stamp_stamp
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         if self.get_queryset().exists() == False:
#             raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')

#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id')))
#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         response = self.list(request, *args, **kwargs)
#         self.get_queryset().delete()
#         return response
    
# class Stamp_DELETE_subelement(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, 
#     """
#     # Stamp_DELETE_subelement
#         SECURITY LEVEL d2
#         - delete the subelement in a project_name.
#     POST params
#         - user_id
#         - project_name
#         - todo_name
#         - subelement_name
#     database changes
#         - targeted subelement will be deleted.
#     """

#     serializer_class = serializers.Stamp_subelement_retrieve
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         # validate existance of stamp_name, user_id
#         query = models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id')))
#         if query.exists() == False:
#             raise exceptions.ValidationError('stamp_name must already exists in the db with the corresponding user_id.')
#         # null check for subelement_name
#         if self.request.POST.get('subelement_name') == '' or self.request.POST.get('subelement_name') == None:
#             raise exceptions.ValidationError('target subelement_name cannot be null or blank')

#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(stamp_name=self.request.POST.get('stamp_name')) 
#                                                  & Q(user_id = self.request.POST.get('user_id'))
#                                                  & Q(subelement_name = self.request.POST.get('subelement_name')))
#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         response = self.list(request, *args, **kwargs)
#         self.get_queryset().delete()
#         return response

# class Stamp_UPDATE_stamp(generics.CreateAPIView, 
#     """
#     # Stamp_UPDATE_stamp
#         SECURITY LEVEL c2
#         - update the stamp, with the target user_id
#         - if X_rename not specified and value is None, then update will not be performed.
#     POST params
#         - user_id -> select
#         - stamp_name -> select
#         - stamp_rename -> update
#     """

#     serializer_class = serializers.Stamp_update_stamp
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()

#         # select target exisistance
#         queryset = models.Stamp.objects.filter(user_id = self.request.POST.get("user_id"),
#                                            stamp_name = self.request.POST.get("stamp_name"))
#         if queryset.exists() == False:
#             raise exceptions.ValidationError('cannot select stamp that was not have been exist.')
        
#         # update target exisistance
#         queryset = models.Stamp.objects.filter(user_id = self.request.POST.get("user_id"),
#                                            stamp_name = self.request.POST.get("stamp_rename"))
#         if queryset.exists() == True:
#             raise exceptions.ValidationError('cannot update stamp to the name that already used by other stamp.')
    

#     def get_queryset(self):
#         self.query_validation()
#         return models.Stamp.objects.filter(user_id = self.request.POST.get("user_id"),
#                                            stamp_name = self.request.POST.get("stamp_name"))
    
#     def post(self, request, *args, **kwargs):
#         # update model
#         stamp_rename = self.request.POST.get("stamp_rename")
#         if stamp_rename == "" or stamp_rename == None: # if rename is null then replace to orig
#             stamp_rename = self.request.POST.get("stamp_name")
#         self.get_queryset().update(stamp_name=self.request.POST.get("stamp_rename"))

#         # make response then return
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
    
# class Stamp_UPDATE_subelement(generics.CreateAPIView, 
#     """
#     # Stamp_UPDATE_subelement
#         SECURITY LEVEL c2
#         - update an subelement on the existing stamp
#         - if named stamp_name is not already exist in db, reject request. 
#     POST params
#         - user_id -> select
#         - stamp_name -> select
#         - subelement_name -> select
#         - subelement_rename -> update
#         - defFunc_rename -> update
#         - arg_names -> update
#         - arg_vals -> update
#     """

#     serializer_class = serializers.Stamp_update_subelement
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         user_id = self.request.POST.get("user_id")
#         stamp_name = self.request.POST.get("stamp_name")

#         # select target exisistance
#         queryset = models.Stamp.objects.filter(user_id = user_id,
#                                            stamp_name = stamp_name)
#         if queryset.exists() == False:
#             raise exceptions.ValidationError('cannot select stamp that was not have been exist.')
        
#         # update target exisistance
#         subelement_rename = self.request.POST.get("subelement_rename")
#         if not(subelement_rename == "" or subelement_rename == None):
#             queryset = models.Stamp.objects.filter(Q(user_id = user_id)
#                                             & Q(stamp_name = stamp_name)
#                                             & Q(subelement_name = subelement_rename)
#                                             & Q(arg_name = ""))
#             if queryset.exists() == True:
#                 raise exceptions.ValidationError('cannot update subelement_rename to the name that already used by other subelements.')
        
#     def get_queryset(self):
#         return models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
#                                             & Q(stamp_name = self.request.POST.get('stamp_name'))
#                                             & Q(subelement_name = self.request.POST.get('subelement_name')))

#     def create(self, request, *args, **kwargs):
#         self.query_validation()

#         user_id = self.request.POST.get('user_id')
#         stamp_name = self.request.POST.get('stamp_name')
#         subelement_name = self.request.POST.get('subelement_name')
#         subelement_rename = self.request.POST.get('subelement_rename')
#         if subelement_rename == None or subelement_rename == "":
#             subelement_rename = subelement_name
#         defFunc_rename = self.request.POST.get('defFunc_rename')
        
#         if defFunc_rename == None or defFunc_rename == "": # for defFunc_rename NULL case, just rename all subelement and its args.
#             if subelement_rename == subelement_name:
#                 pass
#             else:
#                 queryset = models.Stamp.objects.filter(user_id=models.User.objects.get(id=int(user_id)), 
#                                                 stamp_name=stamp_name, 
#                                                 subelement_name=subelement_name)
#                 queryset.update(subelement_name = subelement_rename)
#         else: # for usuall case, delete and re-creation method is applied.


#             # arg_names, arg_vals split with blank
#             arg_names = self.request.POST.get("arg_names")
#             arg_vals = self.request.POST.get("arg_vals")
#             arg_names = arg_names.split(' ')
#             arg_vals = arg_vals.split(' ')

#             # args validation for len()
#             if len(arg_names) != len(arg_vals):
#                 raise exceptions.ValidationError('arg_names and arg_vals must have the same length of elements as sep=\' \'.')

#             # make subelement set dict
#             set_dict = None
#             if defFunc_rename == "discrete_point" :
#                 args_dict = dict(zip(arg_names, arg_vals))
#                 set_dict = sub.Discrete_point.subelement_set(**args_dict)
#             else :
#                 raise exceptions.ValidationError('wrong name : defFunc_name ')


#             # first delete the old arg param
#             targetUser = models.User.objects.get(id=int(user_id))

#             queryset = models.Stamp.objects.filter(user_id=targetUser, 
#                                             stamp_name=stamp_name, 
#                                             subelement_name=subelement_name)
#             queryset.delete()

#             # update arg_rows in models.Stamp
#             for k,v in set_dict.items():
#                 arg_name = k
#                 arg_val = v
#                 models.Stamp.objects.create(user_id=targetUser, 
#                                             stamp_name=stamp_name, 
#                                             subelement_name=subelement_rename,
#                                             defFunc_name = defFunc_rename,
#                                             arg_name = arg_name,
#                                             arg_val = arg_val)

#             models.Stamp.objects.create(user_id=targetUser, 
#                                             stamp_name=stamp_name, 
#                                             subelement_name=subelement_rename,
#                                             defFunc_name = defFunc_rename) # create subelement descriptional row

#             # find all the recode from models.Main which has stamp with user, and tag UNTRUSTED=true.
#             targetStamp = models.Stamp.objects.get(Q(stamp_name = stamp_name)
#                                                 & Q(subelement_name = ""))
#             queryset = models.Main.objects.filter(user_id = targetUser,
#                                                   stamp_id = targetStamp,
#                                                   arg_name = "")
#             for obj in queryset:
#                 date = getattr(obj, "date")
#                 models.Main.objects.create(user_id = targetUser,
#                                         stamp_id = targetStamp,
#                                         date = date,
#                                         arg_name = "untrusted",
#                                         arg_val = True)


#         # make response then return
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=False)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
# #endregion


# #region MAIN_API

# class Main_CREATE_main(generics.CreateAPIView, 
#     """
#     # Main_CREATE_main
#         SECURITY LEVEL c2
#         - create an main recode.
#         - you CAN create the two identical recode in db. they will be count as 2 stamps in the same day
#     POST params
#         - user_id : specific user's id. 
#         - stamp_id : specific stamp_id.
#         - date : date hope to put in the recode
#         - main_vals : vals related to subelements. see the subelement.py 
#     database changes
#         - model Main will get new row of recode.
#         - without arg.
#     """   

#     serializer_class = serializers.Main_main_argsGet
#     permission_classes = [permissions.IsAuthenticated]


#     def query_validation(self):
#         super().query_validation()
#         # validation of existance
#         if self.get_queryset().exists() == True:
#             raise exceptions.ValidationError('cannot add recode that already has been exist.')
        
#         # validation of foregin key relation matching
#         self.serializer_class = serializers.Stamp_all
#         stamp_user = models.Stamp.objects.filter(Q(user_id=self.request.POST.get('user_id'))
#                                                 & Q(id = self.request.POST.get('stamp_id')))
#         if stamp_user.exists() == False:
#             raise exceptions.ValidationError('targeted user must already have the targeted stamp.')
#         self.serializer_class = serializers.Main_main
        
#     def get_queryset(self):
#         queryset = models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
#                                                  & Q(stamp_id = self.request.POST.get('stamp_id'))
#                                                  & Q(date = self.request.POST.get('date')))
#         return queryset
        
#     def create(self, request, *args, **kwargs):
#         self.query_validation()

#         user_id = self.request.POST.get('user_id')
#         stamp_id = self.request.POST.get('stamp_id')
#         date = self.request.POST.get('date')

#         # make subvar dict
#         stamp_stamp = models.Stamp.objects.get(id = int(stamp_id))
#         stamp_name = getattr(stamp_stamp, "stamp_name")
#         stamp_subelements = models.Stamp.objects.filter( Q(user_id = int(user_id))
#                                                         & Q(stamp_name = stamp_name)
#                                                         & ~Q(defFunc_name = '')
#                                                         & Q(arg_name = ''))
#         subvar_dict = None
#         for subelement in stamp_subelements:
#             subelement_name = getattr(subelement, 'subelement_name')
#             if getattr(subelement, 'defFunc_name') == 'discrete_point':
#                 main_vals = self.request.POST.get("main_vals").split(' ')
#                 queryset = models.Stamp.objects.filter( Q(user_id = int(user_id))
#                                                         & Q(stamp_name = stamp_name)
#                                                         & Q(subelement_name = subelement_name)
#                                                         & ~Q(arg_name = ''))
#                 subvar_dict = sub.Discrete_point.subvar_set(queryset, *main_vals)
#             else :
#                 raise exceptions.ValidationError('wrong name : defFunc_name ')

#         for k,v in subvar_dict.items():
#             arg_name = k
#             arg_val = v
#             models.Main.objects.create(user_id = models.User.objects.get(id=int(user_id)), 
#                                         stamp_id = models.Stamp.objects.get(id=int(stamp_id)),
#                                         date = date,
#                                         arg_name = arg_name, 
#                                         arg_val = arg_val,)

#         models.Main.objects.create(user_id = models.User.objects.get(id=int(user_id)), 
#                                     stamp_id = models.Stamp.objects.get(id=int(stamp_id)),
#                                     date = date)
        
#         # make response then return
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

# class Main_DELETE_main(mixins.ListModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView, 
#     """
#     # Main_DELETE_main
#         SECURITY LEVEL d2
#         - delete the recode in a db.
#         - only search for target stamp + date
#     POST params
#         - user_id
#         - stamp_id
#         - date
#     database changes
#         - targeted recode will be deleted.
#     """

#     serializer_class = serializers.Main_main
#     permission_classes = [permissions.IsAuthenticated]

#     def query_validation(self):
#         super().query_validation()
#         # project_name, user_id check
#         if self.get_queryset().exists() == False:
#             raise exceptions.ValidationError('project_name must already exists in the db with the corresponding user_id.')

#     def get_queryset(self):
#         return models.Main.objects.filter(Q(user_id=self.request.POST.get('user_id')) 
#                                                  & Q(stamp_id = self.request.POST.get('stamp_id'))
#                                                  & Q(date = self.request.POST.get('date')))

#     def post(self, request, *args, **kwargs):
#         self.query_validation()
#         response = self.list(request, *args, **kwargs)
#         self.get_queryset().delete()
#         return response


# #endregion
