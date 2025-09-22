"""
@Description :   版本解析
@Author      :   XiaoYuan
@Time        :   2025/09/22 15:01:04
"""
from semantic_version import Version, Spec

def resolve_version(version_spec: str, metadata: dict) -> str | None:
    """
    根据 version_spec 解析出最终版本
    """
    dist_tags = metadata.get("dist-tags", {})
    versions = sorted(
        [Version(v, partial=True) for v in metadata.get("versions", {}).keys()]
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

    return None
