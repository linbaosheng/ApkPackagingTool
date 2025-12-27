#!/usr/bin/env python3
"""
APK 自动重打包工具
使用 apktool 实现 APK 的反编译、修改和重新打包
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
import config


class ApkRepkgError(Exception):
    """APK重打包异常"""
    pass


class ApkRepkg:
    """APK重打包工具类"""

    def __init__(self, apktool_path: str = None):
        """
        初始化APK重打包工具

        Args:
            apktool_path: apktool可执行文件路径，默认使用config.py中的配置
        """
        self.apktool_path = apktool_path or config.APKTOOL_PATH

    def build(self, input_dir: str, output_apk: str) -> str:
        """
        重新打包APK

        Args:
            input_dir: 反编译后的目录路径
            output_apk: 输出APK路径

        Returns:
            打包后的APK文件路径
        """
        input_dir = os.path.abspath(input_dir)
        output_apk = os.path.abspath(output_apk)

        if not os.path.isdir(input_dir):
            raise ApkRepkgError(f"输入目录不存在: {input_dir}")

        manifest_path = os.path.join(input_dir, "AndroidManifest.xml")
        if not os.path.isfile(manifest_path):
            raise ApkRepkgError(f"AndroidManifest.xml 不存在: {input_dir}")

        # 如果是jar文件，使用java -jar运行
        if self.apktool_path.endswith('.jar'):
            cmd = [config.JAVA_PATH, "-jar", self.apktool_path, "b", input_dir, "-o", output_apk, "--use-aapt2"]
        else:
            cmd = [self.apktool_path, "b", input_dir, "-o", output_apk, "--use-aapt2"]

        print(f"[INFO] 正在打包: {input_dir}")
        print(f"[INFO] 输出文件: {output_apk}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise ApkRepkgError(f"打包失败: {result.stderr}")

        print("[INFO] 打包成功")
        return output_apk

    def sign(self, apk_path: str, keystore_path: str,
             storepass: str, alias: str, keypass: Optional[str] = None) -> str:
        """
        签名APK文件

        Args:
            apk_path: 未签名的APK文件路径
            keystore_path: 密钥库文件路径
            storepass: 密钥库密码
            alias: 密钥别名
            keypass: 密钥密码（默认与storepass相同）

        Returns:
            签名后的APK文件路径
        """
        apk_path = os.path.abspath(apk_path)
        keystore_path = os.path.abspath(keystore_path)

        if not os.path.isfile(apk_path):
            raise ApkRepkgError(f"APK文件不存在: {apk_path}")
        if not os.path.isfile(keystore_path):
            raise ApkRepkgError(f"密钥库文件不存在: {keystore_path}")

        keypass = keypass or storepass

        print(f"[INFO] 正在签名: {apk_path}")

        sign_cmd = [
            "jarsigner",
            "-verbose",
            "-sigalg", "SHA256withRSA",
            "-digestalg", "SHA256",
            "-keystore", keystore_path,
            "-storepass", storepass,
            "-keypass", keypass,
            apk_path,
            alias
        ]

        result = subprocess.run(sign_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise ApkRepkgError(f"签名失败: {result.stderr}")

        print("[INFO] 签名成功")
        return apk_path

    def repack(self, input_dir: str, output_apk: str,
               keystore_path: str = None, storepass: str = None,
               alias: str = None) -> str:
        """
        完整重打包流程：打包 -> 签名

        Args:
            input_dir: 反编译后的目录路径
            output_apk: 输出APK路径
            keystore_path: 密钥库文件路径，默认使用config.py配置
            storepass: 密钥库密码，默认使用config.py配置
            alias: 密钥别名，默认使用config.py配置

        Returns:
            重打包并签名后的APK文件路径
        """
        # 使用配置文件默认值
        keystore_path = keystore_path or config.DEFAULT_KEYSTORE
        storepass = storepass or config.DEFAULT_STOREPASS
        alias = alias or config.DEFAULT_ALIAS

        print("=" * 50)
        print("APK 重打包工具")
        print("=" * 50)

        # 1. 打包
        print("\n[步骤 1/2] 打包 APK")
        print("-" * 50)
        built_apk = self.build(input_dir, output_apk)

        # 2. 签名
        print("\n[步骤 2/2] 签名 APK")
        print("-" * 50)
        final_apk = self.sign(built_apk, keystore_path, storepass, alias)

        print("\n" + "=" * 50)
        print("重打包完成！")
        print(f"输出文件: {final_apk}")
        print("=" * 50)

        return final_apk


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="APK自动重打包工具 - 基于apktool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 打包
  python apk_repackager.py build -i decoded/ -o app.apk

  # 签名
  python apk_repackager.py sign -i app.apk

  # 完整流程（打包+签名），使用配置文件默认值
  python apk_repackager.py repack -i decoded/ -o app.apk
        """
    )

    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # build命令
    build_parser = subparsers.add_parser("build", help="重新打包APK")
    build_parser.add_argument("-i", "--input", required=True, help="反编译目录路径")
    build_parser.add_argument("-o", "--output", required=True, help="输出APK路径")
    build_parser.add_argument("--apktool", default=config.APKTOOL_PATH, help=f"apktool路径 (默认: {config.APKTOOL_PATH})")

    # sign命令
    sign_parser = subparsers.add_parser("sign", help="签名APK")
    sign_parser.add_argument("-i", "--input", required=True, help="输入APK路径")
    sign_parser.add_argument("-k", "--keystore", default=config.DEFAULT_KEYSTORE, help=f"密钥库路径 (默认: {config.DEFAULT_KEYSTORE})")
    sign_parser.add_argument("-p", "--storepass", default=config.DEFAULT_STOREPASS, help="密钥库密码")
    sign_parser.add_argument("-a", "--alias", default=config.DEFAULT_ALIAS, help=f"密钥别名 (默认: {config.DEFAULT_ALIAS})")
    sign_parser.add_argument("--keypass", help="密钥密码（默认与storepass相同）")

    # repack命令
    repack_parser = subparsers.add_parser("repack", help="完整重打包流程（打包+签名）")
    repack_parser.add_argument("-i", "--input", required=True, help="反编译目录路径")
    repack_parser.add_argument("-o", "--output", required=True, help="输出APK路径")
    repack_parser.add_argument("--apktool", default=config.APKTOOL_PATH, help=f"apktool路径 (默认: {config.APKTOOL_PATH})")
    repack_parser.add_argument("-k", "--keystore", default=config.DEFAULT_KEYSTORE, help=f"密钥库路径 (默认: {config.DEFAULT_KEYSTORE})")
    repack_parser.add_argument("-p", "--storepass", default=config.DEFAULT_STOREPASS, help="密钥库密码")
    repack_parser.add_argument("-a", "--alias", default=config.DEFAULT_ALIAS, help=f"密钥别名 (默认: {config.DEFAULT_ALIAS})")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "build":
            repkg = ApkRepkg(apktool_path=args.apktool)
            output = repkg.build(args.input, args.output)
            print(f"\n输出: {output}")

        elif args.command == "sign":
            repkg = ApkRepkg()
            output = repkg.sign(args.input, args.keystore, args.storepass, args.alias, args.keypass)
            print(f"\n输出: {output}")

        elif args.command == "repack":
            repkg = ApkRepkg(apktool_path=args.apktool)
            output = repkg.repack(args.input, args.output, args.keystore, args.storepass, args.alias)
            print(f"\n输出: {output}")

        return 0

    except ApkRepkgError as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断")
        return 130
    except Exception as e:
        print(f"[错误] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # PyCharm直接运行模式：使用config.py配置
    if len(sys.argv) == 1:
        try:
            repkg = ApkRepkg()
            repkg.repack(
                input_dir=config.INPUT_DIR,
                output_apk=config.OUTPUT_APK
            )
        except Exception as e:
            print(f"[错误] {e}")
            import traceback
            traceback.print_exc()
    else:
        # 命令行模式
        sys.exit(main())
