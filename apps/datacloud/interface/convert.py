import os
from desire.settings import INTERFACE_DIR

if __name__ == "__main__":
    """
    总控脚本：刷新后台调度
    """
    command1 = os.path.join(INTERFACE_DIR, 'NewRecordConvertToConfig.py')  # 添加新记录时，用于更新后台调度中间表
    command2 = os.path.join(INTERFACE_DIR, 'ValidRecordConvertToETL.py')  # 把记录置为无效时，用于更新后台调度表
    command3 = os.path.join(INTERFACE_DIR, 'ConvertToETL.py')  # 添加和修改记录时，用于更新后台配置表
    command4 = os.path.join(INTERFACE_DIR, 'initializeETL.py')  # 最终调度中间表处理到调度结果表

    os.system(eval('f' + '"' + 'python {command1}' + '"'))
    os.system(eval('f' + '"' + 'python {command2}' + '"'))
    os.system(eval('f' + '"' + 'python {command3}' + '"'))
    os.system(eval('f' + '"' + 'python {command4}' + '"'))

