# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

这是一个基于 Python 的 APK 重打包工具，通过 **apktool** 自动化 APK 的反编译、修改和重新打包流程。这是一个合法的 Android 开发工具，用于应用分析、本地化和修改。

## 架构设计

### 核心组件

- **`apk_repackager.py`**: 主程序，包含 `ApkRepkg` 类及所有核心功能
  - `decode()`: 使用 apktool 反编译 APK
  - `build()`: 从反编译目录重建 APK
  - `sign()`: 使用 jarsigner 签名 APK（可选 zipalign 优化）
  - `repack()`: 完整工作流（反编译 → 打包 → 签名）
  - 基于 argparse 的 CLI 命令行入口

- **`config.py`**: 配置文件，存储路径和默认值

### 工作流程

```
APK 文件 → apktool decode → 反编译目录 → (修改文件) → apktool build → 未签名APK → jarsigner → 已签名APK
```

## 常用命令

### 开发/测试
```bash
# 查看帮助
python apk_repackager.py --help

# 反编译 APK
python apk_repackager.py decode -i app.apk -o decoded/

# 从反编译目录重建 APK
python apk_repackager.py build -i decoded/ -o repacked.apk

# 签名 APK
python apk_repackager.py sign -i repacked.apk --keystore release.keystore --storepass password --alias key0

# 完整重打包流程
python apk_repackager.py repack -i app.apk -o final.apk --sign --keystore release.keystore --storepass password --alias key0
```

### 生成测试密钥库
```bash
keytool -genkey -v -keystore release.keystore -alias key0 -keyalg RSA -keysize 2048 -validity 10000
```

## 外部依赖

此工具**仅使用 Python 标准库**（无需安装 pip 包）。外部工具需单独安装：

| 工具 | 用途 | 是否必需 |
|------|------|----------|
| apktool | APK 反编译/重建 | 是 |
| Java JDK | 运行 apktool 和 jarsigner | 是 |
| jarsigner | APK 签名 | 签名时需要 |
| zipalign | APK 优化 | 可选 |

## 关键实现细节

1. **路径处理**: 内部使用 `pathlib.Path`，subprocess 调用时转换为字符串
2. **错误处理**: 自定义 `ApkRepkgError` 异常提供清晰的错误信息
3. **工具检测**: 自动检查 apktool、java 和 zipalign 的可用性
4. **临时文件**: 使用 `tempfile.mkdtemp()` 为 repack 流程创建临时目录
5. **清理机制**: 支持在重打包后清理工作目录（默认 `clean=True`）

## 扩展工具

如需添加 APK 修改功能：
1. 在 `repack()` 方法的 `decode()` 完成后添加修改逻辑
2. 常见修改目标：
   - `AndroidManifest.xml` - 权限、组件配置
   - `res/` 目录 - 资源文件、字符串、布局
   - `smali/` 目录 - Dalvik 字节码
   - `assets/` 目录 - 嵌入资源
