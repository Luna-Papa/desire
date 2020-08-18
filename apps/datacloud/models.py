from django.db import models
# from smart_selects.db_fields import ChainedForeignKey
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# Create your models here.


class DataSyncTypes(models.TextChoices):
    TYPE_A = 'T+0', 'T+0'
    TYPE_B = 'T+1', 'T+1'
    TYPE_C = 'T+2', 'T+2'
    TYPE_D = 'T+3', 'T+3'


class SyncTypes(models.IntegerChoices):
    """同步状态定义"""
    sync_complete = 1, '已同步'
    sync_waiting = 0, '未同步'
    sync_begin = 2, '开始同步'
    sync_failed = 3, '同步失败'


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
    chn_start_time = models.CharField(verbose_name='渠道加载时间', max_length=5,
                                      help_text='请输入整点或整半点时间，如：01:00、01:30',
                                      validators=[RegexValidator("(20|21|22|23|[0-1]\d):[0,3]0",
                                                                 message='请输入整点或整半点时间，如：01:00、01:30！')])
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    # id字段用于生成后端ETL的作业编号，前台不可见
    chn_id = models.IntegerField(verbose_name='渠道编号', unique=True)
    chn_backup_id = models.IntegerField(verbose_name='渠道备份编号', unique=True)

    def __str__(self):
        return self.chn_name

    class Meta:
        verbose_name = '数据源'
        verbose_name_plural = verbose_name
        ordering = ['chn_id']


class ChkInfo(models.Model):
    """
    条件检测表
    """

    chn_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统名')
    chk_seq = models.IntegerField(verbose_name='检测条件编号', default=0)
    chk_name = models.CharField(verbose_name='检测名称', max_length=128, unique=True)
    chk_condition = models.CharField(verbose_name='检测条件', max_length=256)
    chk_valid_condition = models.CharField(verbose_name='检测有效条件', max_length=128)
    date_type = models.CharField(verbose_name='数据日期', choices=DataSyncTypes.choices, max_length=4,
                                 default=DataSyncTypes.TYPE_B)
    memo = models.CharField(verbose_name='备注', max_length=128, null=True, blank=True)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
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
        ordering = ['chk_id']


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

    chn_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统名')
    chk_name = models.ForeignKey(ChkInfo, on_delete=models.DO_NOTHING, verbose_name='检测名称')
    # chk_name = ChainedForeignKey(ChkInfo, chained_field="chn_name", chained_model_field="chn_name",
    #                              show_all=False, auto_choose=True, sort=True,
    #                              verbose_name='检测名称')
    tab_name = models.CharField(verbose_name='源系统表名', max_length=128)
    exp_method = models.CharField(verbose_name='导出方式', choices=EXP_METHOD_ITEMS,
                                  max_length=10, default='export')
    zl_info = models.CharField(verbose_name='同步标识', choices=(('Z', '增量'), ('Q', '全量')), max_length=1)
    zl_col = models.CharField(verbose_name='增量同步字段', max_length=50, null=True, blank=True)
    ftp_file = models.CharField(verbose_name='FTP同步条件', max_length=256, null=True, blank=True)
    date_type = models.CharField(verbose_name='数据日期', choices=DataSyncTypes.choices, max_length=4,
                                 default=DataSyncTypes.TYPE_B)
    out_path = models.CharField(verbose_name='数据导出目录', max_length=128, null=True, blank=True,
                                validators=[RegexValidator("^\/(\w+)+$", message='请输入合法路径！')])
    outfile_type = models.CharField(verbose_name='数据导出格式', max_length=3,
                                    choices=(('ixf', 'IXF'), ('del', 'DEL')), default='del')
    load_method = models.CharField(verbose_name='加载方式', max_length=20, choices=LOAD_METHOD_ITEMS)
    # increment_flag = models.BooleanField(verbose_name='是否入增量', default=True,
    #                                      help_text='勾选后入增量表，不勾选只入全量表')
    load_tab_tmp = models.CharField(verbose_name='入库增量表名', max_length=128, null=True, blank=True)
    load_tab_mir = models.CharField(verbose_name='入库全量表名', max_length=128, null=True, blank=True)
    month_flag = models.BooleanField(verbose_name='是否仅保留当月数据', default=False,
                                     help_text='勾选后仅保留当月数据，每月2号自动清理，否则一直保留')
    his_flag = models.BooleanField(verbose_name='是否入历史中心',
                                   help_text='勾选后每日自动将数据存入历史表')
    # his_frequency = models.CharField(verbose_name='入历史频次', max_length=1, help_text='输入M（月）或D（天）',
    #                                  null=True, blank=True,
    #                                  validators=[RegexValidator("M|D", message='只能输入M或D')])
    his_frequency = models.CharField(verbose_name='入历史频次', max_length=1, null=True, blank=True,
                                     choices=(('M', '月频度'), ('D', '日频度')))
    his_tab = models.CharField(verbose_name='入历史表名', max_length=128, null=True, blank=True)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    backup_flag = models.BooleanField(verbose_name='备份标识', default=False,
                                      help_text='勾选后每日自动进行备份')
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    sync_id = models.IntegerField(default=100000, verbose_name='数据卸载编号', unique=True)
    load_id = models.IntegerField(default=100000, verbose_name='数据装载编号', unique=True)

    def __str__(self):
        return self.tab_name

    class Meta:
        verbose_name = '数据同步'
        verbose_name_plural = verbose_name
        ordering = ['chn_name', 'chk_name', 'tab_name']


class PushTaskInfo(models.Model):
    """
    数据推送任务信息表
    """
    chn_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统名')
    source_tab_name = models.ForeignKey(SyncTaskInfo, on_delete=models.DO_NOTHING, verbose_name='源系统表名')
    # source_tab_name = ChainedForeignKey(SyncTaskInfo, chained_field="chn_name", verbose_name='源系统表名',
    #                                     chained_model_field="chn_name",
    #                                     show_all=False, auto_choose=True, sort=True)
    # db_name = models.ForeignKey(ChannelInfo, on_delete=models.DO_NOTHING, verbose_name='源系统库名')
    push_type = models.CharField(verbose_name='推送类型', choices=(('TMP', '增量表'), ('MIR', '全量表')),
                                 default='TMP', max_length=3)
    push_tab_name = models.CharField(verbose_name='推送表名', max_length=128)
    path = models.CharField(verbose_name='推送目录', max_length=128,
                            validators=[RegexValidator("^\/(\w+\/?)+$", message='请输入合法路径！')])
    file_type = models.CharField(verbose_name='导出文件格式', max_length=3,
                                 choices=(('ixf', 'ixf'), ('txt', 'txt')))
    code_page = models.CharField(verbose_name='编码格式', max_length=10,
                                 choices=(('1386', '1386'), ('1208', '1208')))
    separator = models.CharField(verbose_name='导出字段分隔符', max_length=10, null=True, blank=True,
                                 help_text='不指定则默认为，')
    delimiter = models.CharField(verbose_name='字段限定符', max_length=10, null=True, blank=True,
                                 help_text='不指定则默认为"')
    # 根据push_tab_name、file_type、code_page、separator、delimiter生成唯一标识
    push_tab_id = models.CharField(verbose_name='推送表标识', max_length=50, unique=True)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    push_id = models.IntegerField(default=100000, verbose_name='数据推送编号')

    def __str__(self):
        return self.push_tab_id

    def clean(self):
        if self.source_tab_name.chn_name != self.chn_name:
            raise ValidationError({'source_tab_name': '表名与数据源不一致！'})

    class Meta:
        verbose_name = '数据推送'
        verbose_name_plural = verbose_name
        ordering = ['chn_name', 'push_tab_id']


class PushSysInfo(models.Model):
    """推送下游系统信息"""
    system_abbr = models.CharField(verbose_name='系统简称', max_length=10, unique=True)
    system_name = models.CharField(verbose_name='系统中文名称', max_length=50)
    push_path = models.CharField(verbose_name='推送路径', max_length=50,
                                 validators=[RegexValidator("^\/(\w+\/?)+$", message='请输入合法路径！')],
                                 help_text='下游系统获取文件目录设置')
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    new_record_flag = models.BooleanField(verbose_name='是否为新记录', default=True)
    push_sys_id = models.IntegerField(verbose_name='推送标识作业编号', default=999980000, unique=True)

    class Meta:
        verbose_name = '下游系统信息'
        verbose_name_plural = verbose_name
        ordering = ['system_name']

    def __str__(self):
        return self.system_name


class PushSysTabInfo(models.Model):
    """推送给下游系统表信息"""
    system_name = models.ForeignKey(PushSysInfo, on_delete=models.DO_NOTHING, verbose_name='系统名称')
    tab_id = models.ForeignKey(PushTaskInfo, on_delete=models.DO_NOTHING,
                               verbose_name='推送表标识')
    channel = models.CharField(verbose_name='数据渠道', max_length=20)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    sync_flag = models.PositiveSmallIntegerField(verbose_name='同步标识',
                                                 default=SyncTypes.sync_waiting, choices=SyncTypes.choices)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')

    class Meta:
        verbose_name = '推送目标定义'
        verbose_name_plural = verbose_name
        ordering = ['system_name', 'channel', 'tab_id']

    def __str__(self):
        return f'{self.system_name}_{self.tab_id}'


class ScriptConfig(models.Model):
    """
    后台SHELL脚本配置表
    """
    type = models.CharField(verbose_name='类别编号', unique=True, max_length=5)
    type_name = models.CharField(verbose_name='任务类型名称', max_length=16, unique=True)
    script = models.CharField(verbose_name='shell脚本配置', max_length=200, unique=True)
    parameter = models.CharField(verbose_name='脚本传入参数', max_length=200, null=True, blank=True,
                                 help_text='多个参数以空格分隔')
    remark = models.CharField(verbose_name='备注', max_length=200, null=True, blank=True)

    def __str__(self):
        return self.type_name

    class Meta:
        verbose_name = '任务分类'
        verbose_name_plural = verbose_name
        ordering = ['type']


class SmsSenderInfo(models.Model):
    """
    短信发送信息表
    """
    name = models.CharField(verbose_name='人员名称', max_length=20)
    phone = models.CharField(verbose_name='手机号', max_length=11)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')
    # sync_flag = models.BooleanField(verbose_name='同步标识', default=False)
    sync_flag = models.IntegerField(choices=SyncTypes.choices, verbose_name='同步标识',
                                    default=SyncTypes.sync_waiting)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '短信发送'
        verbose_name_plural = verbose_name


class ConfigInfo(models.Model):
    """配置表"""
    item = models.CharField(verbose_name='配置项', max_length=50)
    value = models.CharField(verbose_name='配置值', max_length=128)
    describe = models.CharField(verbose_name='配置说明', max_length=128)
    val_flag = models.BooleanField(verbose_name='有效标识', default=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='上次修改时间')

    class Meta:
        verbose_name = '参数配置'
        verbose_name_plural = verbose_name
        ordering = ['item']

    def __str__(self):
        return self.item


class Test001(models.Model):
    chk_name = models.CharField(verbose_name='检测名', max_length=120)
    chn_name = models.CharField(verbose_name='中文名称', max_length=128)

    def __str__(self):
        return self.chn_name

    class Meta:
        verbose_name = '测试'
        verbose_name_plural = verbose_name
