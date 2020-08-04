from django import forms
from .models import SyncTaskInfo
from django.core.exceptions import ValidationError


class SyncTaskInfoAdminForm(forms.ModelForm):
    class Meta:
        model = SyncTaskInfo
        fields = ['chn_name', 'tab_name', 'exp_method', 'zl_info', 'zl_col', 'ftp_file',
                  'outfile_type', 'date_type', 'out_path', 'load_method',
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
        his_flag = self.cleaned_data.get("his_flag")
        his_frequency = self.cleaned_data.get("his_frequency")
        # tab_name = self.cleaned_data.get("tab_name")
        # chn_name = self.cleaned_data.get("chn_name")
        # zl_info = self.cleaned_data.get("zl_info")

        if exp_method == 'ftp' and ftp_file is None:
            raise ValidationError('同步方式为ftp时，ftp条件不允许为空！')
        if his_flag and his_frequency is None:
            raise ValidationError('勾选入历史标识，入历史频次必填')
        # if chn_name == '数据平台' and 'TMP' in tab_name and zl_info == 'Q':
        #     raise ValidationError('入全量数据时，数据平台源需为MIR表')
        else:
            return self.cleaned_data
