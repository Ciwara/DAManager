
import re

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.core import validators

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone


class MemberManager(BaseUserManager):
    def create_user(self, email, username, date_of_birth=None,
                    password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            # date_of_birth=date_of_birth,
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password,
                         email=None, date_of_birth=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            # date_of_birth=date_of_birth,
            username=username,
        )
        user.is_admin = True
        user.is_active = True
        # user.has_perm = True
        user.save(using=self._db)
        return user


class Member(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _('Manager')
        verbose_name_plural = _('Managers')

    username = models.CharField(
        _("username"), max_length=50, primary_key=True,
        help_text=_("Required. 50 characters or fewer. "
                    "Letters, numbers and @/./+/-/_ characters"),
        validators=[validators.RegexValidator(re.compile("^[\w.@+-]+$"),
                                              _("Enter a valid username."),
                                              "invalid")])

    first_name = models.CharField(max_length=100, blank=True, null=True,
                                  verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, blank=True, null=True,
                                 verbose_name=_("Last Name"))
    image = models.ImageField(upload_to='images_member/', blank=True,
                              verbose_name=_("Photo"))
    email = models.EmailField(_("email address"), blank=True, null=True)
    is_staff = models.BooleanField(_("staff status"), default=False,
                                   help_text=_(
        "Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(
        _("active"), default=True,
        help_text=_("Designates whether this user should be treated as "
                    "active. Unselect this instead of deleting accounts."))
    date_of_birth = models.DateField(
        blank=True, null=True, default=timezone.now)
    is_admin = models.BooleanField(default=False)
    objects = MemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name()

    def get_short_name(self):
        return self.name()

    def name(self):
        if not self.first_name and not self.last_name:
            return self.username
        elif not self.first_name:
            return self.last_name
        else:
            return self.first_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Organization(models.Model):

    PREV = 0
    CURRENT = 1
    DEFAULT = 2
    LCONFIG = ((PREV, u"Precedent"),
               (DEFAULT, u"Par defaut"),
               (CURRENT, u"Actuel"),)

    USA = "dollar"
    XOF = "xof"
    EURO = "euro"
    DEVISE = ((USA, "$"), (XOF, "F"), (EURO, "€"))

    member = models.ForeignKey(Member, verbose_name="Utilisateur", blank=True, null=True)
    slug = models.CharField(max_length=100, choices=LCONFIG, default=DEFAULT)
    is_login = models.BooleanField(default=True)
    theme = models.CharField(max_length=100, default=1)
    name_orga = models.CharField(max_length=100, verbose_name=(""))
    phone = models.IntegerField(null=True, verbose_name=(""))
    bp = models.CharField(max_length=100, null=True, verbose_name=(""))
    email_org = models.CharField(max_length=100, null=True, verbose_name=(""))
    adress_org = models.TextField(null=True, verbose_name=(""))
    devise = models.CharField(max_length=100, choices=DEVISE, default=XOF)
    image = models.ImageField(upload_to='images_member/', blank=True,
                              verbose_name=("image de la societe"))

    def __str__(self):
        return self.display_name()

    def display_name(self):
        return u"{} {} {}".format(self.name_orga, self.phone, self.email_org)


class Application(models.Model):

    name = models.CharField(max_length=100, verbose_name="Nom", unique=True)
    description = models.CharField(max_length=200, verbose_name="Description")
    created_date = models.DateField(verbose_name="Date de création")
    public = models.BooleanField(default=False)

    def __str__(self):
        return "App. {} - {}".format(self.name, self.created_date)

    @classmethod
    def get_or_none(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None

    @property
    def get_setups(self):
        return Setup.objects.filter(app=self).order_by("-version_number")

    @property
    def last_setup(self):
        try:
            return self.get_setups[0]
        except:
            return None


class Setup(models.Model):

    app = models.ForeignKey(Application, verbose_name="Application")
    version_number = models.FloatField(verbose_name="numéro de version")
    version_name = models.CharField(
        max_length=20, verbose_name="Nom de version")
    nb_download = models.IntegerField(verbose_name="Download", default=1)
    publish_date = models.DateField(
        verbose_name="Date de publication", default=timezone.now)
    active = models.BooleanField(verbose_name="Active", default=True)
    file = models.FileField(
        upload_to='setups', blank=True, verbose_name=_("Installer"))

    def __str__(self):
        return "{} ver. {} n {}".format(
            self.app, self.version_name, self.version_number)


class Host(models.Model):
    organization = models.ForeignKey(
        Organization, verbose_name="Utilisateur", blank=True, null=True)
    processor = models.CharField(max_length=50, verbose_name="Processeur", blank=True)
    version = models.CharField(max_length=50, verbose_name="Version sys", blank=True)
    node = models.CharField(max_length=50, verbose_name="Note", blank=True)
    platform = models.CharField(max_length=50, verbose_name="platform", blank=True)
    system = models.CharField(max_length=50, verbose_name="system", blank=True)
    ram = models.CharField(max_length=15, verbose_name="RAM", blank=True)
    rom = models.CharField(max_length=15, verbose_name="ROM", blank=True)

    def __str__(self):
        return "{} {}".format(self.node, self.organization)


class License(models.Model):

    host = models.ForeignKey(Host, verbose_name="Machine")
    setup = models.ForeignKey(Setup, verbose_name="Installer")
    code = models.CharField(verbose_name="Code", max_length=15, unique=True)
    isactivated = models.BooleanField(default=True)
    activation_date = models.DateTimeField(
        verbose_name="Date d'activation", default=timezone.now)
    can_expired = models.BooleanField(default=False)
    is_kill = models.BooleanField(default=False)
    expiration_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(
            self.host, self.expiration_date, self.isactivated)
