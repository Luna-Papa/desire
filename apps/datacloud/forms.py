from django import forms
from .models import SyncTaskInfo
from django.core.exceptions import ValidationError


class SyncTaskInfoAdminForm(forms.ModelForm):
    class Meta:
        model = SyncTaskInfo
        fields = ['chn_name', 'chk_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
                  'outfile_type', 'date_type', 'out_path', 'load_method', 'increment_flag',
                  'month_flag', 'backup_flag', 'his_flag', 'his_frequency']

    def clean_tab_name(self):
        # 校验输入表名是否为<schema>.<table_name>格式
        tab_name = self.cleaned_data.get("tab_name").strip()
        if '.' not in tab_name:
            raise ValidationError('请输入带模式名的完整表名！')
        else:
            return tab_name.upper()

    def clean(self):
        exp_method = self.cleaned_data.get("exp_method")
        ftp_file = self.cleaned_data.get("ftp_file")
        if exp_method == 'ftp' and ftp_file is None:
            raise ValidationError('同步方式为ftp时，ftp条件不允许为空！')
        else:
            return self.cleaned_data
