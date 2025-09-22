"""
@Description :   与npm registry交互
@Author      :   XiaoYuan
@Time        :   2025/09/22 14:47:09
"""
import os
import requests

REGISTRY = os.getenv("REGISTRY", "https://registry.npmjs.org")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

def get_package_metadata(name: str):
    """
    获取包的元数据
    """
    url = f"{REGISTRY}/{name}"
    r = requests.get(url, timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        return (False, str(e))
    return (True, r.json())
