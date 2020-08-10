from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


# class UserProfile(AbstractUser):
#
#     gender_choices = (
#         ('male', '男'),
#         ('female', '女')
#     )
#
#     department = models.CharField(verbose_name='所属部门', max_length=64)
#     mobile = models.CharField(verbose_name='手机号码', max_length=11, unique=True)
#     image = models.ImageField(upload_to='image/%Y%m', default='')
