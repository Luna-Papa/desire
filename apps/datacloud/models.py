from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.core.validators import RegexValidator


# Create your models here.


class DataSyncTypes(models.TextChoices):
    TYPE_A = 'T+0', 'T+0'
    TYPE_B = 'T+1', 'T+1'
    TYPE_C = 'T+2', 'T+2'
    TYPE_D = 'T+3', 'T+3'


class ChannelInfo(models.Model):
    """
    数据源信息表
    """
    sys_name = models.CharField(verbose_name='源系统英文简称', max_length=50)
    chn_name = models.CharField(verbose_name='中文名称', max_length=128)
    db_name = models.CharField(verbose_name='数据库名', max_length=128, unique=True)
    address = models.GenericIPAddressField(verbose_name='IP地址')
    port = models.CharField(verbose_name='端口', max_length=20)
    code_page = models.CharField(verbose_name='字符集', max_length=10)
    username = models.CharField(verbose_name='用户名', max_length=50)
    password = models.CharField(verbose_name='密码', max_length=50)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.BooleanField(verbose_name='同步标识', default=False)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    chn_id = models.IntegerField(verbose_name='渠道编号', help_text='自动生成的隐藏列', unique=True)
    # chn_done_id = models.IntegerField(verbose_name='渠道完成编号', help_text='自动生成的隐藏列', unique=True)
    chn_backup_id = models.IntegerField(verbose_name='渠道备份编号', help_text='自动生成的隐藏列', unique=True)

    def __str__(self):
        return self.chn_name

    class Meta:
        verbose_name = '数据源'
        verbose_name_plural = verbose_name


class ChkInfo(models.Model):
    """
    条件检测表
    """

    db_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统库名')
    chk_seq = models.IntegerField(verbose_name='检测条件编号', default=0)
    chk_name = models.CharField(verbose_name='检测名称', max_length=128, unique=True)
    chk_condition = models.CharField(verbose_name='检测条件', max_length=256)
    chk_valid_condition = models.CharField(verbose_name='检测有效条件', max_length=128)
    date_type = models.CharField(verbose_name='数据日期', choices=DataSyncTypes.choices, max_length=4,
                                 default=DataSyncTypes.TYPE_B)
    memo = models.CharField(verbose_name='备注', max_length=128, null=True, blank=True)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.BooleanField(verbose_name='同步标识', default=False)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    chk_id = models.IntegerField(verbose_name='渠道检测编号', help_text='渠道检测调度任务号', unique=True)
    chk_done_id = models.IntegerField(verbose_name='渠道完成编号', help_text='渠道完成调度任务号', unique=True)

    def __str__(self):
        return self.chk_name

    class Meta:
        verbose_name = '检测条件'
        verbose_name_plural = verbose_name


class SyncTaskInfo(models.Model):
    """
    数据同步任务信息表
    """

    # 定义数据卸载格式参数
    EXP_METHOD_ITEMS = (
        ('export', 'export'),
        ('hpu', 'hpu'),
        ('ftp', 'ftp'),
        ('cdc', 'cdc'),
    )

    LOAD_METHOD_ITEMS = (
        ('insert', 'insert'),
        ('insert_update', 'insert_update'),
        ('replace', 'replace'),
        ('delete_insert', 'delete_insert'),
    )

    db_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统库名')
    tab_name = models.CharField(verbose_name='表名', max_length=128)
    # chk_name = models.ForeignKey(ChkInfo, on_delete=models.DO_NOTHING, verbose_name='检测名称')
    chk_name = ChainedForeignKey(ChkInfo, chained_field="db_name", chained_model_field="db_name",
                                 show_all=False, auto_choose=True, sort=True,
                                 verbose_name='检测名称')
    exp_method = models.CharField(verbose_name='导出方式', choices=EXP_METHOD_ITEMS,
                                  max_length=10, default='export')
    zl_info = models.CharField(verbose_name='增量标识', choices=(('Z', '增量'), ('Q', '全量')), max_length=1)
    zl_col = models.CharField(verbose_name='增量同步检测字段', max_length=50, null=True, blank=True)
    ftp_file = models.CharField(verbose_name='FTP同步条件', max_length=256, null=True, blank=True)
    date_type = models.CharField(verbose_name='数据日期', choices=DataSyncTypes.choices, max_length=4,
                                 default=DataSyncTypes.TYPE_B)
    out_path = models.CharField(verbose_name='数据导出目录', max_length=128, null=True, blank=True,
                                validators=[RegexValidator("^\/(\w+)+$", message='请输入合法路径！')])
    outfile_type = models.CharField(verbose_name='数据导出格式', max_length=3,
                                    choices=(('ixf', 'IXF'), ('del', 'DEL')))
    load_method = models.CharField(verbose_name='加载方式', max_length=20, choices=LOAD_METHOD_ITEMS)
    load_tab_tmp = models.CharField(verbose_name='入库增量表名', max_length=128, null=True, blank=True)
    load_tab_mir = models.CharField(verbose_name='入库全量表名', max_length=128, null=True, blank=True)
    month_flag = models.BooleanField(verbose_name='是否仅保留当月数据', default=False,
                                     help_text='勾选后仅保留当月数据，每月2号自动清理；否则一直保留')
    his_flag = models.BooleanField(verbose_name='是否入历史中心',
                                   help_text='勾选后每日自动将数据存入历史表')
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    backup_flag = models.BooleanField(verbose_name='备份标识', default=False,
                                      help_text='勾选后每日自动进行备份')
    sync_flag = models.BooleanField(verbose_name='同步标识', default=False)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    sync_id = models.IntegerField(default=100000, verbose_name='数据卸载编号',
                                  help_text='自动生成的隐藏列', unique=True)
    load_id = models.IntegerField(default=100000, verbose_name='数据装载编号',
                                  help_text='自动生成的隐藏列', unique=True)

    def __str__(self):
        return self.tab_name

    class Meta:
        verbose_name = '数据同步加载任务'
        verbose_name_plural = verbose_name


class PushTaskInfo(models.Model):
    """
    数据推送任务信息表
    """
    db_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统库名')
    source_tab_name = models.ForeignKey(SyncTaskInfo, on_delete=models.DO_NOTHING, verbose_name='源系统表名')
    # db_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统库名')
    push_tab_name = models.CharField(verbose_name='表名', max_length=128,
                                     help_text='实际存储表名，非上游源系统表名')
    path = models.CharField(verbose_name='推送目录', max_length=128)
    file_type = models.CharField(verbose_name='导出文件格式', max_length=3,
                                 choices=(('ixf', 'ixf'), ('txt', 'txt')))
    code_page = models.CharField(verbose_name='编码格式', max_length=10,
                                 choices=(('1386', '1386'), ('1208', '1208')))
    separator = models.CharField(verbose_name='导出字段分隔符', max_length=10, null=True, blank=True,
                                 help_text='不指定则默认为，')
    delimiter = models.CharField(verbose_name='字段限定符', max_length=10, null=True, blank=True,
                                 help_text='不指定则默认为"')
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.BooleanField(verbose_name='同步标识', default=False)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    push_id = models.IntegerField(default=100000, verbose_name='数据推送编号', help_text='自动生成的隐藏列')

    def __str__(self):
        return self.push_tab_name

    class Meta:
        verbose_name = '数据推送任务'
        verbose_name_plural = verbose_name


class ScriptConfig(models.Model):
    """
    后台SHELL脚本配置表
    """
    type = models.IntegerField(verbose_name='类别编号', unique=True)
    script = models.CharField(verbose_name='shell脚本配置', max_length=200)
    parameter = models.CharField(verbose_name='脚本传入参数', max_length=200, help_text='多个参数以空格分隔')

    def __str__(self):
        return self.script

    class Meta:
        verbose_name = '分类任务脚本配置'
        verbose_name_plural = verbose_name
