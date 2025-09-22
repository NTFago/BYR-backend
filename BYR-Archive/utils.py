"""
@Description :   工具方法（content-type 判断等）
@Author      :   XiaoYuan
@Time        :   2025/09/22 15:58:47
"""
import mimetypes

def get_content_type(file_path: str) -> str:
    """
    根据文件路径获取 Content-Type
    """
    mime, _ = mimetypes.guess_type(file_path)
    if mime is None:
        return "application/octet-stream"
    if mime.startswith("text/") or mime in ("application/json", "application/javascript"):
        return f"{mime}; charset=utf-8"
    return mime
