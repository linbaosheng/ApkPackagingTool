"""
APK重打包工具配置文件
"""

# apktool路径配置
APKTOOL_PATH = "./tools/apktool_2.12.1.jar"  # 默认使用系统PATH中的apktool

# Java路径配置
JAVA_PATH = "java"  # 默认使用系统PATH中的java

# Android SDK路径（用于查找apksigner和zipalign）
ANDROID_SDK_PATHS = [
    "ANDROID_HOME",  # 环境变量
    "ANDROID_SDK_ROOT",  # 环境变量
    "~/Android/Sdk",  # Linux默认路径
    "~/Library/Android/sdk",  # macOS默认路径
    "C:\\dev\\android\\sdk",  # Windows默认路径
]

# apksigner路径配置
APKSIGNER_PATH = "C:\\dev\\android\\sdk\\build-tools\\28.0.3\\apksigner.bat"  # Windows使用.bat文件

# zipalign路径配置
ZIPALIGN_PATH = "./tools/zipalign.exe"  # 默认使用系统PATH中的zipalign，可指定完整路径

# 7z 路径配置（用于ZIP打包，比Python zipfile更高效）
SEVEN_ZIP_PATH = "C:\\dev\\setup\\tools\\7-Zip\\7z.exe"  # Windows: "7z" 或完整路径如 "C:\\Program Files\\7-Zip\\7z.exe"

# 默认签名配置
DEFAULT_KEYSTORE = "./tools/test.jks"
DEFAULT_ALIAS = "testkey"
DEFAULT_STOREPASS = "test001"  # 密钥库密码

# 签名方式配置
# V1_ONLY: 仅V1签名(JAR签名), 兼容性最好但体积大
# V2_ONLY: 仅V2签名(APK签名), 体积小, Android 7.0+
# V1_V2: V1+V2双签名, 兼容性和体积平衡
SIGN_MODE = "V2_ONLY"  # 可选: "V1_ONLY", "V2_ONLY", "V1_V2"

# ZIP打包配置
ZIP_COMPRESS_LEVEL = 9  # ZIP压缩级别 (0-9, 9=最高压缩)
ZIPALIGN_ENABLED = True  # 是否启用zipalign对齐优化

# PyCharm直接运行时的配置
INPUT_DIR = "./apk/app"  # 反编译后的目录路径
OUTPUT_APK = "./output/app2.apk"  # 输出APK路径

# 临时文件配置
TEMP_DIR_PREFIX = "apk_repack_"
