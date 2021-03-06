# -*- coding: utf-8 -*-
# @Time : 2022/5/13 8:24
# @Author : Vincent Vic
# @File : FileUploadApiController.py
# @Software: PyCharm
import os

from flask import request, Blueprint

from application import app
from common.lib.CommonResult import CommonResult
from web.service.FileService import FileService

file_upload_api = Blueprint('file_upload_api', __name__)


UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = "app/static/upload"  # 设置文件上传的目标文件夹
basedir = os.getcwd()  # 获取当前项目的绝对路径
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])  # 允许上传的文件后缀

fileService = FileService()

# 判断文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@file_upload_api.route('/file', methods=['POST'], strict_slashes=False)
def api_upload():
    f = request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        uri = fileService.uploadFile(f.read(), ext)
        resp_data = {
            'uri': 'https://flowboot-1301252068.cos.ap-guangzhou.myqcloud.com'+uri
        }
        return CommonResult.successData("上传成功", resp_data)
    else:
        return CommonResult.failMsg("上传失败")
