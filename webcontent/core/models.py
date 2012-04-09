import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils.translation import ugettext_lazy as _
from webcontent.settings import PAGE_TYPE

#   Use south migration tool to generate the migration script.
#   webcontent/manage.py schemamigration core --auto

class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class Member(BaseModel):
    """
    Normal User & Author
    """
    MEMBER_TYPE = (
        (0, 'User'),
        (1, 'Author')
    )

    user = OneToOneField(User, null=True, blank=True)
    handle = models.CharField(max_length=200, unique=True,
        help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"), null=True, blank=True)
    type = models.IntegerField(choices=MEMBER_TYPE, default=0)
    is_auth_active = models.BooleanField(default=False)
    paypal = models.CharField(max_length=50, null=True, blank=True)
    gst_hst = models.CharField(max_length=50, null=True, blank=True)
    money = models.DecimalField(null=False, default=0.0, blank=False, max_digits=10, decimal_places=2)
    commission = models.IntegerField(null=True, blank=True)
    # Email settings
    e_authors = models.BooleanField(default=False)
    e_favourite = models.BooleanField(default=False)
    e_none = models.BooleanField(default=False)


    def __unicode__(self):
        if self.handle:
            return self.handle
        else:
            return self.id


class Tag(BaseModel):
    """
    Tag Management
    """
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return self.name

class FavouriteAuthor(BaseModel):
    """
    Member's favourite Authors
    """
    member = models.ForeignKey(Member)
    author = models.ForeignKey(Member, related_name='+')

    def __unicode__(self):
        return self.member.handle + " favourite " + self.author.handle

class Report(BaseModel):
    """
    Reports Management
    """
    PRICE_TYPE = (
        (0, 'Free'),
        (1, 'Dynamic Pricing'),
        (2, 'Fix Price')
    )
    author = models.ForeignKey(Member)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=250, null=True, blank=True)
    word_count = models.IntegerField()
    page_count = models.IntegerField()
    chart_count = models.IntegerField()
    price_type = models.IntegerField('Price Type', choices=PRICE_TYPE)
    price = models.IntegerField('Start Price', default=0)
    day_rang = models.IntegerField(null=True, blank=True)
    publish_time = models.DateTimeField(default=datetime.datetime.now())
    price_update_time = models.DateTimeField()
    next_update_time = models.DateTimeField(null=True, blank=True)
    is_hide = models.BooleanField(default=False)
    hash_code = models.CharField(max_length=100)

    def current_price(self):
        pass

    def __unicode__(self):
        return self.author.handle + " owns " + self.title

class ReportTagR(models.Model):
    """
    Relationship between Report and Tag
    """
    report = models.ForeignKey(Report)
    tag = models.ForeignKey(Tag, related_name='+')

    def __unicode__(self):
        return self.report.title + " " + self.tag.name

class MyCart(BaseModel):
    """
    My Cart Management
    """
    member = models.ForeignKey(Member)
    report = models.ForeignKey(Report, related_name='+')

    def __unicode__(self):
        return self.member.handle + " " + self.report.title

class SearchFilter(BaseModel):
    """
    Search Filter Management
    """
    filter_name = models.CharField(max_length=30, null=True, blank=True)
    member = models.ForeignKey(Member)
    author = models.CharField(max_length=30, null=True, blank=True)
    report_title = models.CharField(max_length=100, null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    publish_from = models.DateField()
    publish_to = models.DateField()
    is_paid = models.BooleanField()
    paid_from = models.IntegerField(null=True, blank=True)
    paid_to = models.IntegerField(null=True, blank=True)
    is_free = models.BooleanField()

    def __unicode__(self):
        return self.member.handle + "'s filter " + self.filter_name

class TaxSetting(BaseModel):
    """
    Tax Settings Management
    """
    alberta = models.IntegerField()
    british_columbia = models.IntegerField()
    manitoba = models.IntegerField()
    new_brunswick = models.IntegerField()
    newfoundland_labrador = models.IntegerField()
    northwest_territories = models.IntegerField()
    nova_scotia = models.IntegerField()
    nunavut = models.IntegerField()
    ontario = models.IntegerField()
    price_edward_island = models.IntegerField()
    saskatchewan = models.IntegerField()
    quebec = models.IntegerField()

class BottomContent(BaseModel):
    """
    Pick a page and update the custom content div at the bottom of the body
    """
    type = models.IntegerField('Page Type', choices=PAGE_TYPE)
    content = models.CharField(max_length=3000)

    def __unicode__(self):
        return self.type

class Configuration(BaseModel):
    """
    Other Configurations
    """
    footer = models.CharField(max_length=3000)

    def __unicode__(self):
        return 'Configuration'

class HistoryTransaction(BaseModel):
    """
    Transaction History Management
    """
    member = models.ForeignKey(Member)
    report = models.ForeignKey(Report)
    is_free = models.BooleanField()
    is_paid = models.BooleanField(default=True)
    price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    download_url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return self.member.handle + " charge " + self.report.title

class ActiveToken(BaseModel):
    """
    Store email tokens sent when user registers or changes email .
    """
    user = models.ForeignKey(User, null=True)
    token = models.CharField(max_length=256, null=True)