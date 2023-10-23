from django.urls import path

from . import views

urlpatterns = [
    path(route='user/create', view=views.User_CREATE.as_view(), name='user_create'),
    path(route='user/update', view=views.User_UPDATE.as_view(), name='user_update'),

    path(route='project/create/project', view=views.Project_CREATE_project.as_view(), name='project_create_project'),
    # path('project/create/todo', views.Project_CREATE_todo.as_view(), name='project_create_todo'),
    # path('project/retrieve/user', views.Project_RETRIEVE_user.as_view(), name='project_retrieve_user'),
    # path('project/retrieve/project', views.Project_RETRIEVE_project.as_view(), name='project_retrieve_project'),
    # path('project/delete/todo', views.Project_DELETE_todo.as_view(), name='project_delete_todo'),
    # path('project/delete/project', views.Project_DELETE_project.as_view(), name='project_delete_project'),
    
    # path('stamp/create/stamp', views.Stamp_CREATE_stamp.as_view(), name='stamp_create_stamp'),
    # path('stamp/create/subelement', views.Stamp_CREATE_subelement.as_view(), name='stamp_create_subelement'),
    # path('stamp/retrieve/user', views.Stamp_RETRIEVE_user.as_view(), name='stamp_retrieve_user'),
    # path('stamp/retrieve/stamp', views.Stamp_RETRIEVE_stamp.as_view(), name='stamp_retrieve_stamp'),
    # path('stamp/retrieve/subelement', views.Stamp_RETRIEVE_subelement.as_view(), name='stamp_retrieve_subelement'),
    # path('stamp/delete/stamp', views.Stamp_DELETE_stamp.as_view(), name='stamp_delete_stamp'),
    # path('stamp/delete/subelement', views.Stamp_DELETE_subelement.as_view(), name='stamp_delete_subelement'),
    # path('stamp/update/stamp', views.Stamp_UPDATE_stamp.as_view(), name='stamp_update_stamp'),
    # path('stamp/update/subelement', views.Stamp_UPDATE_subelement.as_view(), name='stamp_update_sublement'),

    # path('main/create/main', views.Main_CREATE_main.as_view(), name='main_create_main'),
    # path('main/delete/main', views.Main_DELETE_main.as_view(), name='main_delete_main'),
    
]

