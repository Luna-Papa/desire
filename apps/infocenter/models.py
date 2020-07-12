from django.db import models


# Create your models here.


class SoftwareDefect(models.Model):
    """
    基础软件缺陷清单及检查结果登记
    """

    find_date = models.CharField(verbose_name='发现日期', max_length=6, help_text='示例：201901')
    soft_type = models.CharField(verbose_name='软件类型', max_length=128)
    edition = models.CharField(verbose_name='型号/版本', max_length=20)
    manufactures = models.CharField(verbose_name='生产厂商', max_length=128)
    describe = models.TextField(verbose_name='缺陷描述')
    affect = models.CharField(verbose_name='缺陷影响', max_length=128)
    solution = models.TextField(verbose_name='解决方案')
    patch_version = models.CharField(verbose_name='补丁版本', max_length=20)
    check_result = models.TextField(verbose_name='检查结果', null=True, blank=True)
    suggestion = models.TextField(verbose_name='建议', null=True, blank=True)

    def __str__(self):
        return f'{self.find_date} {self.edition} {self.describe}'

    class Meta:
        verbose_name = '银保监下发基础软件缺陷清单'
        verbose_name_plural = verbose_name

