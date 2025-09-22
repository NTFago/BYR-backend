"""
@Description :   与npm registry交互
@Author      :   XiaoYuan
@Time        :   2025/09/22 14:47:09
"""
from typing import Any
import os
import requests
from cachetools import TTLCache

REGISTRY = os.getenv("REGISTRY", "https://registry.npmjs.org")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

def get_package_metadata(name: str, metadata_cache: TTLCache) -> tuple[bool, Any]:
    """
    获取包的元数据
    """
    if name in metadata_cache:
        return (True, metadata_cache[name])

    url = f"{REGISTRY}/{name}"
    r = requests.get(url, timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        return (False, str(e))
    data = r.json()
    metadata_cache[name] = data
    return (True, data)
