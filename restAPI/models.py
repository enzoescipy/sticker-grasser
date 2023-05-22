from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



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
    Virtual structure : 
        - foregin key user_id
        - sub key project_name
        - list todo
            + todo 1
            + todo 2 
            + ...

    Actual structure :
        - user_id : foregin key from User model.
        - project_name : project name

        - todo_name : todo name
            ~ if todo name == BLANK, this object only define sub_key-project_name.~
            ~ if todo name != BLANK, this object define list-todo elements.~
    """
    user_id = models.ForeignKey('User', related_name='project', on_delete=models.CASCADE, db_column='user_id')
    project_name = models.CharField(max_length=254, unique=False, null=False, blank=False)
    todo_name = models.CharField(max_length=254, unique=False, null=False, blank=True)

    def __str__(self):
        return f"{self.user_id}:{self.project_name}  [{self.todo_name}]"


class Stamp(models.Model):
    """
    Virtual structure:
        - foregin key user_id
        - sub key stamp_name
        - List<tuple> subElements
            + (subelement_name, arg_dict<argname:argval>, definefunc_name)
            + ...
    
    Actual structure:
        - user_id : foregin key 
        - stamp_name : sub key 

        - subelement_name : subElements->subelement_name
        - definefunc_name : subElements->definefunc_name

        - arg_name : subElements-> arg_dict -> key
        - arg_val : subElements-> arg_dict -> val
    """
    user_id = models.ForeignKey('User', related_name='stamp_user', on_delete=models.CASCADE, db_column='user_id')
    stamp_name = models.CharField(max_length=254, unique=False, null=False, blank=False)

    subelement_name = models.CharField(max_length=254, unique=False, null=False, blank=True)
    defFunc_name = models.CharField(max_length=254, unique=False, null=False, blank=True)

    arg_name = models.CharField(max_length=254, unique=False, null=False, blank=True)
    arg_val = models.CharField(max_length=254, unique=False, null=False, blank=True)

    def __str__(self):
        return f"{self.user_id}:{self.stamp_name}  [{self.subelement_name}, {self.defFunc_name}] -> <{self.arg_name}:{self.arg_val} >"
    

class Main(models.Model):
    """
    Virtual structure:
        - foregin key user_id

        - foregin key stamp_id
        - datetime user selected date

        - dict<argname:argval> stamp_subval
    
    Actual structure
        - foregin key user_id

        - foregin key stamp_id
        - datetime user selected date

        - arg_name : arg_dict -> key
        - arg_val : arg_dict -> val
    """

    user_id = models.ForeignKey('User', related_name='main_user', on_delete=models.CASCADE, db_column='user_id')

    stamp_id = models.ForeignKey('Stamp', related_name='main_stamp', on_delete=models.DO_NOTHING , db_column='stamp_id',
                                 limit_choices_to={"subelement_name": ''})
    date = models.DateField(unique=False, null=True, blank=True)

    arg_name = models.CharField(max_length=254, unique=False, null=False, blank=True)
    arg_val = models.CharField(max_length=254, unique=False, null=False, blank=True)

    def __str__(self):
        return f"{self.user_id}:{self.stamp_id}:{str(self.date)}   <{self.arg_name}:{self.arg_val} >"
    
