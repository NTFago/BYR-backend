# 2025 BYR Team 后端考核

## BYR-Archive
### 设计思路
1. URL 路由规则设计
    用户访问 URL，需要解析成三个部分：
    - `/包名[@版本][/子路径]`
    - 包名：支持 scope，比如 `@babel/core`
    - 版本：没写就取 `latest` (registry 里的 dist-tags.latest)
    - 子路径：没写就说明访问的是入口文件（要解析 package.json）
    例如：
    - `/react → react@latest` 的入口文件
    - `/lodash@4.17.21/lib/index.js` → 直接取该文件
    - `/vue@3.3.4/` → 展示该包版本根目录列表

2. registry 交互
    如果设置了`REGITSTRY`环境变量，就使用私有registry，否则默认使用`https://registry.npmjs.org`

    主要调用点如下：
    1. 获取包元信息： `GET {registry}/{package}`
        - 包含`versions`、`dist-tags`、每个版本的`dust.tarball`
    2. 解析需要的版本:
        - `/react` → 查找`dist-tags.latest`
        - `/react@19.1.1` → 直接用`versions["19.1.1"]`
    3. 下载 tarball:
        - `versions[v].dist.tarball`
        - 解压到本地缓存目录

3. 入口文件解析
    当访问`/包名`或`/包名@版本`，要找到入口文件：
    1. 读`package.json`
    2. 按顺序判断：
        - 有`exports["."]` → 取`"default"`段或字符串
        - 否则看`main`
        - 否则fallback到`index.js`
    3. 返回文件内容，并附带**Content-Type**

