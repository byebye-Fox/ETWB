[TOC]
# django

django做后端主要是用于使用python作为后端主要语言的情况，我只按照最简单的方法来讲对应的配置。

## 建立一个django项目

如果使用pycharm进行开发，在File->New project->Django中选择对应的配置,location中设置的是存储路径和对应的项目名称，application名称为对应的app名称	，之后create就ok了。

#### 项目目录结构

**假设建立的项目名称为Project1，建立的application名称为APP1。**

则项目目录结构为：

Project1:项目的容器

  	 ---  _init_.py：一个空文件，告诉python该目录是一个python包

  	 ---  settings.py  ：该Django项目的设置/配置

   	---  urls.py：该Django项目的URL声明；一份又Django驱动的网站‘目录’

  	 ---  wsgi.py：一个WSGI兼容的web服务器的入口，以便于运行你的项目

templates：存放html页面的位置

APP1：APP应用的名称，可以多个，此处只是以zhuce这个应用举例说明。

　　--- migrations：记录models的变更记录。

　　--- models ：通过面向对象的思路编写数据操作指令（可以简单理解为编写数据库脚本文件的）

​    	--- views：编写系统业务逻辑的位置。

​		 (其他文件没啥用)

manage.py：一个实用的命令行工具，可以让你以各种方式与该Django项目进行交互

## 配置

1、基础配置

​	打开Project1->settings.py文件，在ALLOWED_HOST中设置对应IP地址，在INSTALLED_APP中加入app的名称。使用pycharm可能不需要这一步，保险起见还是看一下的好。host的地址应该是本机的ip地址

2、如果使用数据库

​	同样在settings文件下，DATABASES中配置所使用的数据库名称，账户名，和密码。（name,user,password）

3、项目运行

​	在项目目录下，python manage.py runserver，之后便可在对应的host下看到，默认的本地调试端口是127.0.0.1:8000。

#### app配置

1、如果使用数据库，需要对app进行建表和字段设置。在APP1的models文件中

进行数据库字段建立的方法为继承django中自带的model类。

```python
from django.db import models

class TESTCLASS(models.Model):
    name = models.ChartField(max_length=30)
    password = models.ChartField(max_length=30)
	
    def __str__(self):
        return self.name
```

运行项目，上面的代码就会建立一个表单，名称为APP1_TESTCLASS。其中有两个字段，分别是name和password。

2、路由设置

所谓路由设置，就是对于url进行判定，判定前端请求具体由哪部分代码处理。咱们这个应用，应该不需要多个app，所以接口同一订到一个app下应该就可以了。现在假设有一个请求，请求url为"/search/"，假设处理该请求的函数名称为CLsearch，该函数应当被放置在APP1->views文件中。

首先打开Project1->urls文件，在文件头加入如下代码

```python
import APP1.views as mv
```

在urlpatterns中加入path

```python
path('search/',mv.CLsearch)
```

在views文件中，如果前端和后端都是用http协议的话，要加入对应的引用

```python
from django.http import JsonResponse,HttpResponseRedirect
```

对于search请求，后端在收到该请求之后就会转到APP1.views中寻找CLsearch函数来处理该请求，对于请求在views文件中可以使用类似的处理方式。

```python
def search(request):
    theDATA =request.GET
   	attr1DATA = theDATA["attr1"]
    attr2DATA = theDATA["attr2"]
    ...
    
    res = DoSomeOperation(attr1DATA,attr2DATA,...)
    # res是字典，或者json形式都ok，至于编码问题，需要前端和后端统一一下。

    return JsonResponse(res)
```

如果需要使用数据库中的内容，则需要对服务器端进行post请求以获取结果，如下代码，便可获取对应的name的值。

```python
from APP1.models import TESTCLASS
from django.core.exceptions import ObjectDoesNotExist

def getpassword(request):
    name1 = "name1"
    # 或者是从request中获取的对应的数据
    try:
        person = TESTCLASS.objects.get(name = name1)
        # 可以理解为这是对数据库进行一次见多，person获取的是name=name1的结果
    except ObjectDoesNotExist:
        TESTCLASS.objects.create(name=name1 , password="")
        # 数据库中没有该项，可以建立一项
    else:
        DoSomething(person)
        # 找到了对应的项，可以对变量person进行操作
```

参考项：https://blog.csdn.net/ymeddmn/article/details/76407253，其中关于数据返回前端的方法，使用这个博客里的方法也是可以的，网上两种方法都可。



整体的流程应该就是这些，主要注意的就是url配置的问题，url配置ok的话，前后端只要能连起来，就不会有什么大问题了。