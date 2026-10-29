from langchain_core.tools import tool

@tool
def read_file(path:str):
    """
    This is a function to read a file
    The parameters is:
    :param path: The path of the file
    This function returns the content of the file
    """

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@tool
def write_file(path:str,content:str):
    """
    This is a function to write a file
    The parameters are:
    :param path: the path of the file
    :param content: the content of the file
    This function returns if the file was written
    """
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'wrote to {path}'

@tool
def replace_file(path:str,old_content:str,new_content:str,allow_multiple_edits:bool=False):
    """
    This is a function to replace a file
    The parameters are:
    :param path: The path of the file
    :param old_content: The content of the file
    :param new_content: The new content to be written
    :param allow_multiple_edits: Boolean to Allow multiple edits if True or not allow multiple edits if False
    This function returns if the file was replaced
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    count=content.count(old_content)
    if count==0:
        return f'old string not found in {path}'
    if count>1 and not allow_multiple_edits:
        return f'old string found in {path} ,{count} times, add surrounding lines to make it unique or enable multiple edits'

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.replace(old_content,new_content))
    return f'replaced {count} match(es) into {path}'