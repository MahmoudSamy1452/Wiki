from django.shortcuts import render
from django.http import HttpResponse
from . import util
from random import randint
import re


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content == None:
        return render(request,'encyclopedia/404.html')
    return render(request, 'encyclopedia/entry.html',{
        "title": title,
        "content": conversion(content)
    })

def search(request):
    entries = util.list_entries()
    result = [i for i in entries if request.POST['q'].lower() in i.lower()]
    if not len(result):
        result.append(request.POST['q'])
    elif result[0].lower() != request.POST['q'].lower():
        return render(request, 'encyclopedia/results.html',{
            "results":result
        })
    return entry(request, result[0])

def random(request):
    entries = util.list_entries()
    index = randint(0, len(entries)-1)
    return entry(request, entries[index])

def add_entry(request):
    if request.method == 'POST':
        if request.POST['Title'] in util.list_entries():
            return render(request, 'encyclopedia/exists.html')
        util.save_entry(request.POST['Title'], request.POST['Content'])
        return entry(request, request.POST['Title'])
    return render(request, 'encyclopedia/add.html')

def edit_entry(request, title):
    if request.method == 'POST':
        util.save_entry(title, request.POST['Content'])
        return entry(request, title)
    return render(request, 'encyclopedia/edit.html', {
        "title": title,
        "content": util.get_entry(title)
    })

def conversion(content):

    # headings
    p = re.compile(r'#{1,6}[\S\s]*?\r\n')
    iterator = p.finditer(content)
    content = list(content)
    n = 0
    for match in iterator:
        count = content[int(match.start()):int(match.end())].count('#')
        content.insert(int(match.start())+n,f'<h{count}>')
        content.insert(int(match.end())-1+n,f'</h{count}>')
        n+=2
    content = [i for i in content if i != '#']
    content = ''.join(content)

    # line breaks
    content = content.replace('\r\n','<br>')

    # anchors
    match = re.search(r'\[[\s\w]+?\]\([\s\S]+?\)(?!\))', content)
    while match:
        link = content[content.find("(",int(match.start()))+1:int(match.end())-1]
        x = re.sub(r'\[', f'<a href="{link}">', content[int(match.start()):int(match.end())])
        x = re.sub(r'\]\([\s\S]+?\)(?!\))', '</a>', x)
        content = content[:int(match.start())]+x+content[int(match.end()):]
        match = re.search(r'\[[\s\w]+?\]\([\s\S]+?\)(?!\))', content)
    
    #Bold
    while content.find('**') != -1:
        content = content.replace('**',"<strong>", 1)
        content = content.replace('**',"</strong>", 1) 
               
    #Unordered List
    match = re.search(r'[\+\-\*] [\s\S]*?<br>', content)
    if match:
        content = list(content)
        content.insert(int(match.start()), '<ul>')
        content = ''.join(content)
        last = int(match.end())
        match = re.search(r'[\+\-\*] [\s\S]*?<br>', content)
        while match:
            last = int(match.end())
            x = re.sub(r'[\+\-\*] ', f'<li>', content[int(match.start()):int(match.end())])
            x = re.sub(r'<br>', '</li>', x)
            content = content[:int(match.start())]+x+content[int(match.end()):]
            match = re.search(r'[\+\-\*] [\s\S]*?<br>?', str(content))
        content = list(content)
        content.insert(last+3, '</ul>')
    
    #Paragraph
    content = ''.join(content)
    match = re.search(r'<br>(?!<br>)(?!<p>)(?!<h)(?!<ul>)[\s\S]+?(?!<br>)[\s\S]+?<br>', content)
    while match:
        content = list(content)
        content.insert(int(match.start())+4, '<p>')
        if content[int(match.start()):int(match.end())+1][-4:] == list('<br>'):
            content.insert(int(match.end())-3, '</p>')
        else:
            content.insert(int(match.end())+1, '</p>')
        content = ''.join(content)
        match = re.search(r'<br>(?!<br>)(?!<p>)(?!<h)(?!<ul>)[\s\S]+?(?!<br>)[\s\S]+?<br>', content)
    return ''.join(content)
