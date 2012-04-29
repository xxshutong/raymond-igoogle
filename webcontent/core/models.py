from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import OneToOneField

#   Use south migration tool to generate the migration script.
#   webcontent/manage.py schemamigration core --auto

GADGETS_TYPE = (
    ('Facebook', 'Facebook'),
    ('Twitter', 'Twitter'),
    ('Myspace', 'Myspace'),
    ('Gmail', 'Gmail'),
    ('Hotmail', 'Hotmail'),
    ('YahooMail', 'Yahoo mail'),
    ('CNN', 'CNN'),
    ('BBC', 'BBC')
)

LIBRARY_TYPE = (
    (' SocialNetworking', ' Social Networking'),
    ('Email', 'Email'),
    ('NewsFeed ', 'News Feed ')
)

class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class UserProfile(BaseModel):
    """
    Normal User
    """
    user = OneToOneField(User, null=True, blank=True)
    full_name = models.CharField(max_length=50)
    birthday = models.DateField()
    ic_num = models.CharField(max_length=50)

    def __unicode__(self):
        return self.full_name

class Gadgets(BaseModel):
    """
    Gadgets Management
    """
    name = models.CharField(max_length=30, unique=True)
    type = models.CharField('Gadgets Type', choices=GADGETS_TYPE, max_length=50)

    def __unicode__(self):
        return self.name



class Library(BaseModel):
    type = models.CharField('Library Type', choices=LIBRARY_TYPE, max_length=50)
    gadget = models.ForeignKey(Gadgets, name='gadget')

    def __unicode__(self):
        return self.type + ' - ' + self.gadget.name

class Tab(BaseModel):
    user_profile = models.ForeignKey(User, name='user_profile')
    name = models.CharField(max_length=30)
    order = models.IntegerField(null=True, blank=True)

class TabGadgetsR(BaseModel):
    tab = models.ForeignKey(Tab, name='tab')
    gadget = models.ForeignKey(Gadgets, name='gadget')
    column = models.IntegerField()
    row = models.IntegerField()
    title = models.CharField(max_length=20, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    color_class = models.CharField(max_length=30, default='color-green')

