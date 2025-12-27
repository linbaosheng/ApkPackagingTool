"""
APK重打包工具配置文件
"""

# apktool路径配置
APKTOOL_PATH = "./tools/apktool_2.9.1.jar"  # 默认使用系统PATH中的apktool

# Java路径配置
JAVA_PATH = "java"  # 默认使用系统PATH中的java

# Android SDK路径（用于查找zipalign）
ANDROID_SDK_PATHS = [
    "ANDROID_HOME",  # 环境变量
    "ANDROID_SDK_ROOT",  # 环境变量
    "~/Android/Sdk",  # Linux默认路径
    "~/Library/Android/sdk",  # macOS默认路径
    "D:\\soft\\dev\\Android\\Sdk",  # Windows默认路径
]

# 默认签名配置
DEFAULT_KEYSTORE = "./tools/test.jks"
DEFAULT_ALIAS = "testkey"
DEFAULT_STOREPASS = "test001"  # 密钥库密码

# PyCharm直接运行时的配置
INPUT_DIR = "./apk/ttm2"  # 反编译后的目录路径
OUTPUT_APK = "./output/app.apk"  # 输出APK路径

# 临时文件配置
TEMP_DIR_PREFIX = "apk_repack_"
