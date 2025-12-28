# APK 自动重打包工具

Python 实现的 APK 重打包工具，支持 **apktool 方式**和 **ZIP 方式**两种打包模式。

## 功能特性

| 方式 | 命令 | 适用场景 |
|------|------|----------|
| **apktool 方式** | `build` / `repack` | 需要修改 `AndroidManifest.xml`、资源文件、Smali 代码 |
| **ZIP 方式** | `zip-build` / `repack-zip` | 添加 DEX 文件、简单替换资源（更快、体积更小） |

- 两种打包模式：apktool 重建 / 直接 ZIP 压缩
- 灵活的签名配置：V1 / V2 / V1+V2
- 自动 zipalign 对齐优化
- 支持 7z 高效压缩
- PyCharm 一键运行

## 环境要求

| 工具 | 用途 | 是否必需 |
|------|------|----------|
| Python 3.6+ | 运行脚本 | 是 |
| Java JDK | 运行 apktool/apksigner | 是 |
| apktool | APK 反编译/重建 | apktool 方式需要 |
| 7z | ZIP 高效压缩 | 推荐（体积更小） |
| zipalign | APK 对齐优化 | 可选 |
| apksigner | APK 签名 | 签名需要 |

## 快速开始

### 1. 配置 `config.py`

```python
# 输入输出配置
INPUT_DIR = "./apk/app"      # 解压后的APK目录
OUTPUT_APK = "./output/app.apk"  # 输出APK路径

# 签名配置
DEFAULT_KEYSTORE = "./tools/test.jks"
DEFAULT_ALIAS = "testkey"
DEFAULT_STOREPASS = "test001"

# 签名方式（影响APK体积）
SIGN_MODE = "V2_ONLY"  # "V1_ONLY" | "V2_ONLY" | "V1_V2"

# 7z 路径（用于ZIP打包）
SEVEN_ZIP_PATH = r"C:\dev\setup\tools\7-Zip\7z.exe"
```

### 2. PyCharm 一键运行

直接在 PyCharm 中运行 `apk_repackager.py`，会显示菜单：

```
==================================================
APK 重打包工具 - PyCharm 运行模式
==================================================
输入目录: ./apk/app
输出APK:  ./output/app.apk
密钥库:   ./tools/test.jks
==================================================

请选择操作模式:
  1. apktool 方式 (repack) - 反编译目录 → apktool重建 → 签名
  2. ZIP 方式 (repack-zip)  - 解压目录 → 直接压缩 → 签名

输入选择 (1 或 2，默认 1):
```

## 命令行使用

### apktool 方式

```bash
# 打包
python apk_repackager.py build -i decoded/ -o app.apk

# 完整流程（打包+签名）
python apk_repackager.py repack -i decoded/ -o app.apk
```

### ZIP 方式（推荐用于添加DEX）

```bash
# ZIP打包（不签名）
python apk_repackager.py zip-build -i extracted/ -o app.apk

# ZIP方式完整流程（压缩+签名）
python apk_repackager.py repack-zip -i extracted/ -o app.apk

# 跳过zipalign对齐（更快但APK稍大）
python apk_repackager.py repack-zip -i extracted/ -o app.apk --no-align
```

### 签名

```bash
python apk_repackager.py sign -i app.apk \
    --keystore release.keystore \
    --storepass password \
    --alias key0
```

## 两种打包方式区别

| 特性 | apktool 方式 | ZIP 方式 |
|------|-------------|----------|
| 输入目录 | apktool 反编译的目录 | unzip 解压的目录 |
| 目录特征 | 有 `apktool.yml`，二进制 XML | 原始结构，明文 XML |
| 处理流程 | apktool 重建 APK | 直接 ZIP 压缩 |
| 速度 | 较慢 | 更快 |
| 适用场景 | 修改资源、清单、Smali | 添加 DEX、简单替换 |

## 配置说明

### 签名方式 `SIGN_MODE`

| 模式 | 体积 | 兼容性 | 说明 |
|------|------|--------|------|
| `V2_ONLY` | 最小 | Android 7.0+ | 推荐 |
| `V1_ONLY` | 大 | 所有版本 | 仅旧设备 |
| `V1_V2` | 中等 | 所有版本 | 兼容性最好 |

### ZIP 压缩配置

```python
ZIP_COMPRESS_LEVEL = 9    # 压缩级别 (0-9)
ZIPALIGN_ENABLED = True   # 是否对齐优化
```

## 生成密钥库

```bash
keytool -genkey -v -keystore release.keystore -alias key0 \
    -keyalg RSA -keysize 2048 -validity 10000
```

## 常见问题

**Q: APK 体积变大了？**
- 检查 `SIGN_MODE` 是否设为 `V2_ONLY`
- 确保 7z 路径配置正确
- 打包目录中不要有旧的 `META-INF` 签名文件

**Q: 选择哪种打包方式？**
- 用 apktool 反编译的 → 用模式 1 (apktool)
- 用 unzip 解压的 → 用模式 2 (ZIP)

**Q: 如何添加 DEX 文件？**
1. 用 unzip 解压 APK
2. 将 `classes2.dex` 等放入根目录
3. 使用 ZIP 方式打包

## 项目结构

```
PackagingTool/
├── apk_repackager.py   # 主程序
├── config.py           # 配置文件
├── apk/                # 输入目录
├── output/             # 输出目录
└── tools/              # 工具文件
    ├── apktool_2.12.1.jar
    ├── test.jks
    └── zipalign.exe
```
