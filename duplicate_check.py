SAVE_PATH_DIR = "./爬取结果/"
md5_save_path = SAVE_PATH_DIR + "md5.txt"
md5_load_path = SAVE_PATH_DIR + "md5.txt"

print("duplicate_check模块:当前md5保存目录为:", md5_save_path)
print("duplicate_check模块:当前md5读取目录为:", md5_load_path)
print("duplicate_check模块:调用change_save_path,change_load_path进行路径更改")
print('+'*100)

import os
import hashlib


def get_long_sentences(text_list):
    '''
    从全文列表中获取最长的五个句子
    :param text_list: 全文列表
    '''
    count = 5
    text_list.sort(key=lambda x: len(x), reverse=True)
    return text_list[:count]


def get_md5(sentence):
    '''
    将列表中的字符串进行md5处理
    :param sentence: 文章的一段话
    :return: md5值
    '''

    md5 = hashlib.md5()
    md5.update(bytes(sentence, encoding='utf-8'))

    return md5.hexdigest()


def write_md5(md5):
    '''
    将md5写入文件
    :param md5: md5值
    '''
    if not os.path.exists(SAVE_PATH_DIR):
        os.mkdir(SAVE_PATH_DIR)
    with open(md5_save_path, 'a') as f:
        f.write(md5)
        f.write("\n")


def load_md5():
    '''
    读取md5库
    :return: md5列表
    '''
    with open(md5_load_path, 'r') as f:
        md5_list = f.read().splitlines()
    return md5_list


def change_save_path(save_path):
    '''
    改变保存路径(注意：路径文件夹需要存在)
    :param save_path: 自定义保存路径
    '''
    global md5_save_path

    md5_save_path = save_path


def change_load_path(load_path):
    '''
    改变保存路径(注意：路径文件夹需要存在)
    :param save_path: 自定义保存路径
    '''
    global md5_load_path

    md5_load_path = load_path


def md5_comparison(md5_value, md5_lib):
    '''
    将单条md5与md5库对比
    :param md5_value: md5值
    :param md5_lib: 从文件读取的列表形式md5库
    :return: 布尔值
    '''

    if md5_value in md5_lib:
        return False
    else:
        return True


def duplicate_check(text_list):
    '''
    对一篇文章进行查重，将不重复的md5值写入md5库
    :param text_list: 全文列表
    :return: 文章重复，返回False否则返回True
    '''
    count = 0

    try:
        md5_lib = load_md5()
    except:
        print("未找到md5库文件，自动将读取路径设置为保存路径，或尝试调用change_load_path重新指定路径")
        md5_lib = []
        global md5_save_path
        global md5_load_path
        md5_load_path = md5_save_path

    long_sentences = get_long_sentences(text_list)
    for sentence in long_sentences:
        md5_value = get_md5(sentence)
        if md5_comparison(md5_value, md5_lib):
            write_md5(md5_value)
        else:
            count += 1

    if count > 3:
        print("文章重复句子数为：{}，不予收录".format(count))
        return False
    else:
        print("文章重复句子数为：{}，收录".format(count))
        return True