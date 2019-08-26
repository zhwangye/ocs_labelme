# coding:utf-8
from tkinter import messagebox as tkmsgbox
"""
帮助菜单
使用说明和其他信息
"""
def onMenuItem_About():
    helpMsg = '打标程序V1.0\n\n' \
              '运行条件:\n' \
              '同级目录**须有** img，txt 和 point 文件夹\n' \
              './img/目录下放置需要标注的图片\n\n' \
              '1：正常，    2：倾斜\n' \
              'z: 上一张,    x：下一张\n' \
              'c：清除点，    v：确认点\n' \
              'space：c+v,    /：退出\n' \
              '鼠标右键：c+v    滚轮：z | x\n\n' \
              'author：zhwangye\n' \
              'date：2019/05/03'
    tkmsgbox.showinfo(message=(helpMsg))