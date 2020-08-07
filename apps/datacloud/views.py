from django.shortcuts import render
from django.http import JsonResponse
from .models import ChannelInfo, ChkInfo
# Create your views here.


def choose_chk_info(request):
    """
    查询检测条件
    :param request:
    :return:
    """
    if request.method == 'GET':
        chn = request.GET.get('chn_name')
        if chn:
            checks = list(ChkInfo.objects.filter(chn_name=chn).values("chk_name"))
            return JsonResponse(checks, safe=False)


def get_chk_name(request, name=None):
    if request.method == 'GET':
        if not name:
            names = list(ChkInfo.objects.filter(val_flag=True).values("chk_name"))
        else:
            names = list(ChkInfo.objects.filter(val_flag=True, chk_name__contains=name).values("chk_name"))
        return JsonResponse(names, safe=False)
