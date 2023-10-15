from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

"""

Terminology

    - Declaring "(temp)" first makes it a temporary field, and there is no need to implement it.
    - "pkey" refers to the primary key of the model in question.
    - The "XX model fkey" denotes a foreign key that references the "pkey" of the "XX" model.
    - When a model named "AAOwnedBB" is defined, it signifies a model that acts as a bridge, implying that, in terms of meaning, "AA" owns multiple "BB"s.
    - If model "BB" has a "UNIQUE" field while "AA" exists, it implies that duplicate checking must be performed following these steps:
        1. Find the owner "AA" of "BB" in "AAOwnedBB."
        2. Find all "BB"s belonging to "AA."
    - The fields of the found "BB"s must not have duplicates with each other.
    - If model "RR" has a "UNIQUE" field while "XX YY" exists, it means that:
        1. In "XXYYOwnedRR," find the owners "XX & YY" of "RR."
        2. Find all the "RR"s owned by "XX & YY" (by locating the "RR" foreign keys in all columns where "XX" and "YY" are referenced as foreign keys).
        3. The fields of the found "RR"s must not have duplicates with each other.
        4. If there is a "CASE," only a few specified options are valid inputs.
    
    developer has the korean lang. terminology in his notion doc.
"""


#region User model

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
    
#endregion

#region Project model

"""
Virtual structure : 
    - foregin key user_id
    - sub key project_name
    - list todo
        + todo 1
        + todo 2 
        + ...
"""

class Project(models.Model):
    """
    Project model.
    the collection of todo's.

    Structure : 
        - pkey
        - User model fkey (CASCADE)
        - project_name (UNIQUE by each User)

    """
    user_fkey = models.ForeignKey('User', related_name='project_user', on_delete=models.CASCADE, db_column='user_fkey')
    project_name = models.CharField(max_length=254, unique=False, null=False, blank=False)

    def __str__(self):
        return f"{self.user_id}:{self.project_name}"

class Todo(models.Model):
    """
    Todo model.
    the to-do you want to relate with the stamp and record the pass/fail by time.

    Structure : 
        - pkey
        - Project model fkey (CASCADE)
        - todo_name (UNIQUE by each Project)
    """
    project_fkey = models.ForeignKey('Project', related_name='todo_project', on_delete=models.CASCADE, db_column='project_fkey')
    todo_name = models.CharField(max_length=254, unique=False, null=False, blank=False)

    def __str__(self):
        return f"{self.project_fkey}:{self.todo_name}"
#endregion

#region Stamp

"""
Virtual structure:
    - foregin key user_id
    - sub key stamp_name
    - List<tuple> subElements
        + (subelement_name, arg_dict<argname:argval>, definefunc_name)
        + ...
"""

class Stamp(models.Model):
    """
    Stamp model.
    setting the stamp which user will use when checking the pass/fail of the todo.
    
    Structure:
        - pkey
        - User model fkey (CASCADE)
        - stamp_name (UNIQUE by each User)
    """
    user_fkey = models.ForeignKey('User', related_name='stamp_user', on_delete=models.CASCADE, db_column='user_fkey')
    stamp_name = models.CharField(max_length=254, unique=False, null=False, blank=False)

    def __str__(self):
        return f"{self.user_fkey}:{self.stamp_name}"

class DefFunc(models.Model):
    """
    DefFunc model.
    choose the pre-built process function that will handle the stamp record.
    for example, if you choose the 
        defFunc_name = "discrete_point"
    , this means that Stamp will not only mark the pass/fail of the work, but also
    count the some amount of point that is done with that work.
    eg : page of the book you read 

    Structure:
    - pkey
    - Stamp model fkey
    - defFunc_name (CASE)
    """
    stamp_fkey = models.ForeignKey('Stamp', related_name='defFunc_stamp', on_delete=models.CASCADE, db_column='stamp_fkey')
    defFunc_name = models.CharField(max_length=254, unique=False, null=False, blank=False)

    def __str__(self):
        return f"{self.stamp_fkey}:{self.defFunc_name}"
    
class FuncArg(models.Model):
    """
    FuncArg model.
    set the choosen function's optional arguments.
    for example, if you chose the "discrete_point" in the DefFunc model,
    FuncArg option can be like,
        arg_name : value = "is_accmulated" : True
    which means, the point will be accumulated besides, so that you can see the total point you got
    from this stamp.

    Structure:
        - pkey
        - DefFunc model fkey
        - arg_name (UNIQUE while DefFunc)
        - arg_value
    """
    stamp_fkey = models.ForeignKey('DefFunc', related_name='funcArg_defFunc', on_delete=models.CASCADE, db_column='defFunc_fkey')
    arg_name = models.CharField(max_length=254, unique=False, null=False, blank=False)
    arg_value = models.CharField(max_length=254, unique=False, null=False, blank=False)

    def __str__(self):
        return f"{self.stamp_fkey}:{self.arg_name}:{self.arg_value} "
    

#endregion
"""
Virtual structure:
    - foregin key user_id
    - foregin key todo_id
    - foregin key stamp_id

    - datetime user selected date
    - dict<argname:argval> stamp_subval
"""

class UserTodoStampOwnedHistory(models.Model):
    """
    UserTodoStampOwnedHistory model.
    relate the {User * Todo * Stamp} to the {History} model.
    this model's each row has its own pkey, so that even if the identical combination of {User * Todo * Stamp} exists,
    the each of a row meaning the diffrent History log.

    Structure:
        - pkey
        - User model fkey
        - Stamp model fkey
        - Todo model fkey
        - History model fkey
    """
    user_fkey = models.ForeignKey('User', related_name='userTodoStampOwnedHistory_user', on_delete=models.CASCADE, db_column='user_fkey')
    stamp_fkey = models.ForeignKey('Stamp', related_name='userTodoStampOwnedHistory_stamp', on_delete=models.DO_NOTHING, db_column='stamp_fkey')
    todo_fkey = models.ForeignKey('Todo', related_name='userTodoStampOwnedHistory_todo', on_delete=models.DO_NOTHING, db_column='todo_fkey')
    history_fkey = models.ForeignKey('History', related_name='userTodoStampOwnedHistory_history', on_delete=models.CASCADE, db_column='history_fkey')

    def __str__(self):
        return f"{self.user_fkey}:{self.stamp_fkey}:{self.todo_fkey}:{self.history_fkey} "
    
class History(models.Model):
    """
    History model
    the log for the, which todo is stamped by which stamp, on which user!
    
    Structure:
        - pkey
        - date string
        
    """
    date = models.DateField(unique=False, null=True, blank=True)

    def __str__(self):
        return f"{self.date}"

class HistoryArg(models.Model):
    """
    HistoryArg model
    For some cases, information of just "is stamp stamped?" is not enough to represent its defFunc(e.g : page of books that you read) function. 
    this model privides the additional information for the stamping history.

    Structure:
        - pkey
        - History model fkey
        - arg_name (UNIQUE while History)
        - arg_val

    """

    history_fkey = models.ForeignKey('History', related_name='userTodoStampOwnedHistory_history', on_delete=models.CASCADE, db_column='history_fkey')
    arg_name = models.CharField(max_length=254, unique=False, null=False, blank=False)
    arg_value = models.CharField(max_length=254, unique=False, null=False, blank=False)
    
    def __str__(self):
        return f"{self.history_fkey}:{self.arg_name}:{self.arg_value}"