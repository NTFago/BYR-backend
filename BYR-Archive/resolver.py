"""
@Description :   解析入口文件、URL 到实际文件路径
@Author      :   XiaoYuan
@Time        :   2025/09/22 15:01:04
"""
import os
import json
from semantic_version import Version, Spec

def resolve_version(version_spec: str, metadata: dict) -> str | None:
    """
    根据 version_spec 解析出最终版本
    """
    dist_tags = metadata.get("dist-tags", {})
    versions = sorted(
        [Version(v) for v in metadata.get("versions", {}).keys()]
    )

    # 1. 没指定 → latest
    if not version_spec or version_spec == "latest":
        return dist_tags.get("latest", str(versions[-1]))

    # 2. dist-tag
    if version_spec in dist_tags:
        return dist_tags[version_spec]

    # 3. 精确版本
    if version_spec in metadata["versions"]:
        return version_spec

    # 4. semver range (^、~、>= ...)
    try:
        spec = Spec(version_spec)
        matched = [v for v in versions if v in spec]
        if matched:
            return str(matched[-1])  # 最新符合条件的版本
    except Exception:
        pass

    # 没找到符合的版本
    return None

def resolve_entry_file(root_dir: str) -> str:
    """
    处理 package.json，找出入口文件
    """
    pkg_json = os.path.join(root_dir, "package.json")
    if not os.path.exists(pkg_json):
        return "index.js"

    with open(pkg_json, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    # 处理experts["."]
    if "exports" in pkg and "." in pkg["exports"]:
        exp = pkg["exports"]["."]
        if isinstance(exp, dict) and "default" in exp:
            return exp["default"].lstrip("./")
        if isinstance(exp, str):
            return exp.lstrip("./")

    # 无exports，处理main字段
    if "main" in pkg:
        return pkg["main"].lstrip("./")

    # fallback到index.js
    return "index.js"
