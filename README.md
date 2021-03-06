# 社区服务 Python 服务端
## 一、技术及依赖
### 框架依赖
- Flask 2.1.2
- Flask-SQLAlchemy 2.5.1
- mysqlclient 2.1.0
- redis 4.2.2
- Flask sqlacodegen 1.1.8
- Jinja 3.1.2

# 设施依赖
- Mysql 5.7 
- Redis 6.0

## 二、启动
```shell
python -m flask run
```
## 三、目录结构
```shell
+---app
|   |   application.py # web应用核心
|   +---common
|   |   +---lib # 通用库
|   +---config # 配置
|   +---docs # 文档
|   +---jobs #定时任务
|   +---static # 静态文件，css和js
|   +---templates # 静态模板
|   +---web
|   |   +---controller
|   |   |   +---admin # 管理员后台控制器
|   |   |   +---api # 小程序接口控制器
|   |   +---model 
|   |   +---service
+---tests # 测试文件
|   .flaskenv # 环境配置
|   app.py # 启动入口
|   README.md # 子树文件
|   requirements.txt # 环境依赖
```

## 四、model 生成
> 使用 flask-sqlacodegen 扩展 方便快速生成 ORM model 
> 
```shell
pip install flask-sqlacodegen
```

**使用方法**
```shell
flask-sqlacodegen 'mysql://root:root@127.0.0.1/community_service' --outfile "common/models/model.py"  --flask

flask-sqlacodegen 'mysql://root:root@127.0.0.1/community_service' --tables user --outfile "app/web/model/user.py"  --flask
```		

## 对应前端小程序
[小程序](https://github.com/Vincent-Vic/community-service-mini)
