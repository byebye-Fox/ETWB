from django.shortcuts import render
import markdown
import formatter



# Create your views here.

def show_introduction(request):
    content = ""
    with open("./static/assets/md/introduction.md","r",encoding='utf-8') as f:
        content = markdown.markdown(f.read(),
             extensions=[
                # 包含 缩写、表格等常用扩展
                'markdown.extensions.extra',
                # 语法高亮扩展
                'markdown.extensions.codehilite',
                #toc是目录
                'markdown.extensions.toc',
        ]
        )
        # content = formatter(f.read(),filter_name = "markdown")
    return render(request,"introduction/introduction.html",{"content":content})










