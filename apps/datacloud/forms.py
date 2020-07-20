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
        tab_name = self.cleaned_data.get("tab_name").strip()
        if '.' not in tab_name:
            raise ValidationError('请输入带模式名的完整表名！')
        else:
            return tab_name.upper()
