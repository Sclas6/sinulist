import dropbox
from file_mng import *
import json
from sec import *

def gen_json(contents, title):
    content_num = 0
    contains = 10
    content = '{"type":"carousel","contents":['
    content_size = len(contents)
    pages = int(content_size / contains) + 1
    for i in range(1, pages if contains == 1 else pages + 1):
        content += '{"type":"bubble","header":{"type":"box","layout":"vertical","contents":[{"type":"text","text":"'
        content += f"{title} {i}/{pages}"
        content += '","size": "xxl"}]},"body":{"type":"box","layout":"vertical","spacing": "sm","contents":[{"type":"text","wrap":true,"weight":"regular","size":"md","text":"'
        for j in range(contains):
            content += rf"・ {contents[content_num]}\n"
            content_num += 1
            if content_num >= content_size:
                break
        content += '","maxLines": 20}]}},'
    content = content[:-1]
    content += ']}'
    return json.loads(content)

def checkls(list, kakumono):
    juuhuku=False
    for n in range(len(list)):
        if kakumono == list[n]:
            juuhuku = True
    if juuhuku == True:
        return True
    else:
        return False

def addlist(list, kakumono):
    list.append(kakumono)
    make_pkl(list, "list")

def rmlist(list, kakumono):
    list.remove(kakumono)
    make_pkl(list, "list")

def rmrecent(list):
    str = list[-1]
    rmlist(list, list[-1])
    return str

def rmnum(list, num):
    str = list[num - 1]
    rmlist(list[num - 1])
    return str

def pic_checkls(list, content):
    for n in list:
        if content == n:
            return True
    return False

def pic_save(list, kaitamono, content):
    client = dropbox.Dropbox(ACCESS_TOKEN)
    with open(f'{kaitamono}.jpg','wb') as f:
        for chunk in content.iter_content():
            f.write(chunk)
    #upload
    with open(f'{kaitamono}.jpg','rb') as f:
        client.files_upload(f.read(), f'/{kaitamono}.jpg', mode = dropbox.files.WriteMode.overwrite)
    #del
    os.remove(f'{kaitamono}.jpg')
    #create link
    setting = dropbox.sharing.SharedLinkSettings(requested_visibility = dropbox.sharing.RequestedVisibility.public)
    link = client.sharing_create_shared_link_with_settings(path = f'/{kaitamono}.jpg', settings=setting)
    #get link
    links = client.sharing_list_shared_links(path = f'/{kaitamono}.jpg', direct_only = True).links
    if links is not None:
        for link in links:
            url = link.url
            url = url.replace('www.dropbox','dl.dropboxusercontent').replace('?dl=0','')
    list[kaitamono] = url
    make_pkl(list, "kaita")

def pic_rmlist(list, kesumono):
    list.pop(kesumono)
    make_pkl(list, "kaita")