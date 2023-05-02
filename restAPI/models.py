from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    AbstractUser model, but email added.
    """
    email = models.EmailField(max_length=254)

    # id (int) : PK
    # username (char) : user id
    # email (char) : email
    # password (char) : encrypted password
    # is_staff (bool) : if admin then true, false for else
    # is_active (bool) : activated user the true
    # is_superuser (bool) : if true then this user is superuser
    # last_login : (datetime) last login time
    # date_joined : (datetime) time that this user has been created.

    def __str__(self):
        return self.username

class Project(models.Model):
    """
    there are project that has children 'todo's.
    todo is some works or jobs have to be solved, and project is set of todos.
    Project model is the table that has todo and project both.
    if col has projectname="study", todoname="math", it means this col is the description of study->math.
    ant if projectname="study", todoname=NULL, it means this col is the description of study project itself.
    """
    user_id = models.ForeignKey('User', related_name='project', on_delete=models.CASCADE, db_column='user_id')
    project_name = models.CharField(max_length=254, unique=False, null=False, blank=False)
    todo_name = models.CharField(max_length=254, unique=False, null=False, blank=True)

    def __str__(self):
        return self.project_name + "-[" + self.todo_name + "]"


