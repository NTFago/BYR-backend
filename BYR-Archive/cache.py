"""
@Description :   缓存处理
@Author      :   XiaoYuan
@Time        :   2025/09/22 19:19:16
"""
import os
import shutil
import tarfile
import tempfile
import requests
from cachetools import TTLCache

metadata_cache = TTLCache(maxsize=1000, ttl=3600)   # 包元信息缓存
dir_cache = TTLCache(maxsize=2000, ttl=600)         # 目录索引缓存

CACHE_DIR = os.getenv("CACHE_DIR", "./cache")

def ensure_package_cached(name: str, version: str, metadata: dict) -> str | None:
    """下载并缓存包 tarball，返回本地路径"""
    name = name.strip("/")
    root_dir = os.path.join(CACHE_DIR, f"{name.replace('/', '_')}@{version}")
    if os.path.exists(root_dir):
        return root_dir

    tarball_url = metadata["versions"][version]["dist"]["tarball"]
    os.makedirs(CACHE_DIR, exist_ok=True)

    # 下载 tarball
    with requests.get(tarball_url, stream=True) as r:
        try:
            r.raise_for_status()
        except requests.HTTPError:
            return None
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
            tar_path = f.name

    # 解压
    with tarfile.open(tar_path, "r:gz") as tar:
        tmp_dir = root_dir + ".tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        tar.extractall(tmp_dir)
        extracted_dir = os.path.join(tmp_dir, "package")
        shutil.move(extracted_dir, root_dir)
        shutil.rmtree(tmp_dir)
    os.remove(tar_path)

    return root_dir
