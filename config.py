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

# d8 工具路径配置（用于 DEX 转换，支持 JAR/AAR 转 DEX）
D8_PATH = "C:\\dev\\android\\sdk\\build-tools\\28.0.3\\d8.bat"  # Windows: d8.bat，Linux/Mac: d8

# android.jar 路径配置（d8 转换时的 boot classpath）
ANDROID_JAR_PATH = "C:\\dev\\android\\sdk\\platforms\\android-28\\android.jar"

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

# AAR 转 DEX 配置
INPUT_AAR = "./aar/PluginJar.aar"  # 输入AAR文件路径
OUTPUT_DEX = "./output/classes.dex"  # 输出DEX文件路径

# DEX 反编译/编译配置
INPUT_DEX = "./dex/classes.dex"  # 输入DEX文件路径
OUTPUT_SMALI_DIR = "./smali/out"  # 输出Smali目录路径
INPUT_SMALI_DIR = "./smali/out"  # 输入Smali目录路径（用于编译）
COMPILED_DEX = "./output/compiled.dex"  # 编译后的DEX文件路径

# baksmali/dex2jar 工具路径配置（DEX 反编译）
# 选项1: baksmali (将 DEX 反编译为 Smali 代码)
BAKSMALI_PATH = "./tools/baksmali-2.1.3.jar"  # baksmali.jar 路径
# 选项2: dex2jar (将 DEX 转换为 JAR，可用 JD-GUI 查看)
DEX2JAR_PATH = "./tools/dex2jar.jar"  # d2j-dex2jar.bat 或 dex2jar.jar 路径

# smali 工具路径配置（Smali 代码编译为 DEX）
SMALI_PATH = "./tools/smali-2.1.3.jar"  # smali.jar 路径

# 临时文件配置
TEMP_DIR_PREFIX = "apk_repack_"
