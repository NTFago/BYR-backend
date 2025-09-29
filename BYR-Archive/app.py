"""
@Description :   jsDelivr 服务模拟
@Author      :   XiaoYuan
@Time        :   2025/09/22 15:56:04
"""
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from registry import get_package_metadata
from resolver import resolve_version, resolve_entry_file
from utils import get_content_type
from cache import ensure_package_cached, metadata_cache, dir_cache
from local_logger import logger


app = FastAPI()

@app.middleware("http")
async def log_requests(request, call_next):
    """
    日志系统
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(
        "%s %s %s status=%d time=%.2fms",
        request.client.host, request.method, request.url.path,
        response.status_code, process_time
    )

    return response

@app.get("/{path:path}")
async def serve(path: str):
    """
    路由规则:
      /pkg
      /pkg/
      /pkg@version
      /pkg@version/file.js
      /pkg@version/
    """
    if not path:
        return HTMLResponse(str({}), status_code=200)


    # 解析包名、版本、文件路径
    ## 有版本号
    if "@" in path and not path.startswith("@"):
        pkg, rest = path.split("@", 1)
        ## 版本号带具体文件
        if "/" in rest:
            version_spec, sub_path = rest.split("/", 1)
        ## 版本号不带具体文件
        else:
            version_spec, sub_path = rest, ""
        package_name = pkg
    elif path.startswith("@"):
        parts = path.split("/", 2)
        package_name = parts[0] + "/" + parts[1]
        rest = parts[2] if len(parts) > 2 else ""
        version_spec, sub_path = "latest", rest
    ## 无版本号带具体文件
    elif "/" in path and not path.endswith("/"):
        pkg, rest = path.split("/", 1)
        package_name = pkg
        version_spec, sub_path = "latest", rest
    ## 无版本号无具体文件
    else:
        package_name, version_spec, sub_path = path, "latest", ""

    package_name = package_name.strip("/")
    version_spec = version_spec.strip().strip("/")
    sub_path = sub_path.strip().strip("/")

    logger.info(
        "Parsed: package_name=%s, version_spec=%s, sub_path=%s",
        package_name, version_spec, sub_path
    )

    metadata = get_package_metadata(package_name, metadata_cache)
    if not metadata[0]:
        logger.error("Failed to fetch metadata for package '%s': %s",
                     package_name, metadata[1])
        raise HTTPException(502, f"Error fetching metadata: {metadata[1]}")
    metadata = metadata[1]

    version = resolve_version(version_spec, metadata)
    if version is None:
        logger.error("Version '%s' not found for package '%s'",
                     version_spec, package_name)
        raise HTTPException(404, f"Version '{version_spec}' not found for package '{package_name}'")

    root_dir = ensure_package_cached(package_name, version, metadata)
    if root_dir is None:
        logger.error("Failed to download tarball for package '%s' version '%s'",
                     package_name, version)
        raise HTTPException(502, "Error downloading package tarball")

    logger.info("Serving package '%s' version '%s' from '%s'",
                package_name, version, root_dir)

    # 目录
    if path.endswith("/"):
        file_path = root_dir
        if file_path in dir_cache:
            files = dir_cache[file_path]
        else:
            try:
                files = os.listdir(file_path)
                dir_cache[file_path] = files
            except FileNotFoundError as exc:
                logger.error("Directory not found: %s", file_path)
                raise HTTPException(404, "Directory not found") from exc
        links = "".join(
            f'<li><a href="{name}">{name}</a></li>' for name in files
        )
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{package_name}</title></head>
<body><h1>{package_name}@{version}</h1><hr><ul>{links}</ul><hr></body></html>
"""
        return HTMLResponse(content=html, status_code=200)

    # 处理入口文件
    if not sub_path:
        res, entry = resolve_entry_file(root_dir)
        if not res:
            logger.error("Entry file not found in package '%s' version '%s'", package_name, version)
            raise HTTPException(404, entry)
        file_path = f"{root_dir}/{entry}"
    else:
        file_path = f"{root_dir}/{sub_path}"

    logger.debug("Resolved file path: %s", file_path)


    # 文件
    if not os.path.exists(file_path) :
        logger.error("File not found: %s", file_path)
        raise HTTPException(404, f"File not found: {sub_path}")
    return FileResponse(file_path, media_type=get_content_type(file_path))
