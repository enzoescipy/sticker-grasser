from django.urls import path

from . import views

urlpatterns = [
    path('user/retrieve/<str:username>', views.User_RETRIEVE.as_view(), name='user_retrieve'),
    path('user/create', views.User_CREATE_unauthorized.as_view(), name='user_create'),
    path('project/create/project', views.Project_CREATE_project.as_view(), name='project_create_project'),
    path('project/create/todo', views.Project_CREATE_todo.as_view(), name='project_create_todo'),
    path('project/retrieve/user/<int:user_id>', views.Project_RETRIEVE_user.as_view(), name='project_retrieve_user'),
    path('project/retrieve/project', views.Project_RETRIEVE_project.as_view(), name='project_retrieve_project'),
    path('project/delete/todo', views.Project_DELETE_todo.as_view(), name='project_delete_todo'),
    path('project/delete/project', views.Project_DELETE_project.as_view(), name='project_delete_project'),
]