from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have email")
        if not username:
            raise ValueError("User must have username")
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
                email = self.normalize_email(email),
                password = password,
                username = username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    ##
    # Only need the URL and CRN for one class   


    ##Input fields when authenticated
    subject = models.CharField(max_length=5, default='DefaultSubject')
    term = models.CharField(max_length=10, default='DefaultTerm')
    crn = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm (self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
class WatchedClass(models.Model):
    # because I assigned this relationship,
    # i can now access, subject, term, and crn which are held
    # temporarily within account
    account = models.ForeignKey(
        Account, related_name="watchedclasses",
        on_delete=models.DO_NOTHING
        )
    
    crn = models.IntegerField(default=0)
    url = models.CharField(max_length=100, default='DefaultTerm')
    title = models.CharField(max_length=100, default='DefaultTerm')


    def __str__(self):
        return(
            f"{self.title} "
            f"{self.crn} "
            f"{self.url} "
            )
