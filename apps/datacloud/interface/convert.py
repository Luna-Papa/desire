import os
from desire.settings import INTERFACE_DIR

if __name__ == "__main__":
    """
    刷新后台调度总控脚本
    """
    command1 = os.path.join(INTERFACE_DIR, 'new_record_convert.py')
    command2 = os.path.join(INTERFACE_DIR, 'update_record_convert.py')
    command3 = os.path.join(INTERFACE_DIR, 'valid_record_convert.py')
    command4 = os.path.join(INTERFACE_DIR, 'initialize.py')

    os.system(eval('f' + '"' + 'python {command1}' + '"'))
    os.system(eval('f' + '"' + 'python {command2}' + '"'))
    os.system(eval('f' + '"' + 'python {command3}' + '"'))
    os.system(eval('f' + '"' + 'python {command4}' + '"'))

