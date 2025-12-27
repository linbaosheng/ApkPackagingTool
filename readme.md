# APK 自动重打包工具

Python 通过 apktool 实现 APK 自动化重打包。

## 功能特性

- **反编译 (decode)**: 使用 apktool 反编译 APK 文件
- **重新打包 (build)**: 将反编译后的目录重新打包成 APK
- **签名 (sign)**: 使用 jarsigner 对 APK 进行签名
- **完整流程 (repack)**: 一键完成反编译、打包、签名的完整流程

## 环境要求

1. **Python 3.6+**
2. **apktool**: [下载地址](https://ibotpeaches.github.io/Apktool/)
3. **Java JDK**: 用于运行 apktool 和 jarsigner
4. **Android SDK** (可选): 用于 zipalign 优化

## 安装

```bash
# 克隆项目
git clone <repository_url>
cd PackagingTool

# 无需额外安装Python依赖（仅使用标准库）
```

## 使用方法

### 反编译 APK

```bash
python apk_repackager.py decode -i app.apk -o decoded/
```

### 重新打包 APK

```bash
python apk_repackager.py build -i decoded/ -o repacked.apk
```

### 签名 APK

```bash
python apk_repackager.py sign -i repacked.apk -o signed.apk \
    --keystore release.keystore \
    --storepass your_password \
    --alias key0
```

### 完整重打包流程

```bash
python apk_repackager.py repack -i app.apk -o final.apk
```

### 重打包并签名

```bash
python apk_repackager.py repack -i app.apk -o final.apk --sign \
    --keystore release.keystore \
    --storepass your_password \
    --alias key0
```

## 项目结构

```
PackagingTool/
├── apk_repackager.py   # 主程序文件
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
└── readme.md          # 说明文档
```

## 命令行参数

| 命令 | 参数 | 说明 |
|------|------|------|
| decode | -i, --input | 输入APK文件路径 |
| | -o, --output | 输出目录路径 |
| | -f, --force | 强制覆盖已存在的输出目录 |
| build | -i, --input | 输入反编译目录路径 |
| | -o, --output | 输出APK文件路径 |
| | --no-aapt2 | 不使用aapt2 |
| sign | -i, --input | 输入APK文件路径 |
| | -o, --output | 输出APK文件路径 |
| | --keystore | 密钥库文件路径 |
| | --storepass | 密钥库密码 |
| | --alias | 密钥别名 |
| repack | -i, --input | 输入APK文件路径 |
| | -o, --output | 输出APK文件路径 |
| | -w, --workdir | 工作目录路径 |
| | --no-clean | 不清理工作目录 |
| | --sign | 签名APK |

## 生成密钥库

如需签名APK，先生成密钥库：

```bash
keytool -genkey -v -keystore release.keystore -alias key0 -keyalg RSA -keysize 2048 -validity 10000
```