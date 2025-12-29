#!/usr/bin/env python3
"""
APK 自动重打包工具
使用 apktool 实现 APK 的反编译、修改和重新打包
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path
from typing import Optional
import config


class ApkRepkgError(Exception):
    """APK重打包异常"""
    pass


class ApkRepkg:
    """APK重打包工具类"""

    def __init__(self, apktool_path: str = None, apksigner_path: str = None, zipalign_path: str = None):
        """
        初始化APK重打包工具

        Args:
            apktool_path: apktool可执行文件路径，默认使用config.py中的配置
            apksigner_path: apksigner可执行文件路径，默认使用config.py中的配置
            zipalign_path: zipalign可执行文件路径，默认使用config.py中的配置
        """
        self.apktool_path = apktool_path or config.APKTOOL_PATH
        self.apksigner_path = apksigner_path or config.APKSIGNER_PATH
        self.zipalign_path = zipalign_path or config.ZIPALIGN_PATH

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
            cmd = [config.JAVA_PATH, "-jar", self.apktool_path, "b", input_dir, "-o", output_apk]
        else:
            cmd = [self.apktool_path, "b", input_dir, "-o", output_apk]

        print(f"[INFO] 正在打包: {input_dir}")
        print(f"[INFO] 输出文件: {output_apk}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise ApkRepkgError(f"打包失败: {result.stderr}")

        print("[INFO] 打包成功")
        return output_apk

    def zip_build(self, input_dir: str, output_apk: str, align: bool = True) -> str:
        """
        通过ZIP方式重新打包APK（不使用apktool）

        直接将解压的目录重新压缩为APK，适用于添加DEX文件等场景。
        优先使用 7z 压缩，回退到 Python zipfile。

        Args:
            input_dir: 解压后的APK目录路径
            output_apk: 输出APK路径
            align: 是否进行zipalign对齐优化（默认True）

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

        # 先删除可能存在的旧文件
        if os.path.exists(output_apk):
            os.remove(output_apk)

        # 尝试使用 7z 压缩（更高效）
        seven_zip = getattr(config, 'SEVEN_ZIP_PATH', '7z')
        try:
            return self._zip_build_with_7z(input_dir, output_apk, seven_zip, align)
        except FileNotFoundError:
            print(f"[INFO] 7z 不可用，使用 Python zipfile...")
            return self._zip_build_with_python(input_dir, output_apk, align)

    def _zip_build_with_7z(self, input_dir: str, output_apk: str, seven_zip: str, align: bool) -> str:
        """使用 7z 压缩（更高效，体积更小）"""
        print(f"[INFO] 正在打包 (7z方式): {input_dir}")

        # 需要不压缩的文件扩展名
        store_extensions = {
            '.dex', '.so', '.png', '.jpg', '.jpeg', '.gif', '.webp',
            '.mp3', '.mp4', '.ogg', '.arsc'
        }

        # 构建文件列表
        files_to_add = []
        for root, dirs, files in os.walk(input_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__MACOSX']
            if 'META-INF' in dirs:
                dirs.remove('META-INF')

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, input_dir).replace('\\', '/')
                files_to_add.append((file_path, arcname))

        # 使用 7z 命令压缩
        temp_list_file = os.path.join(input_dir, '_7z_file_list.txt')
        try:
            with open(temp_list_file, 'w', encoding='utf-8') as f:
                for file_path, arcname in files_to_add:
                    ext = os.path.splitext(file_path)[1].lower()
                    # 不压缩的文件用 -mx0
                    if ext in store_extensions or os.path.basename(file_path) in ('resources.arsc', 'AndroidManifest.xml'):
                        f.write(f'{file_path}\n')
                    else:
                        f.write(f'{file_path}\n')

            # 7z 命令：创建 ZIP，使用 DEFLATE，最高压缩
            cmd = [
                seven_zip, 'a', '-tzip',
                f'-mx={config.ZIP_COMPRESS_LEVEL}',
                '-mfb=256',
                '-mpass=15',
                '-r',
                output_apk,
                f'{input_dir}\\*'
            ]

            # 排除 META-INF 和隐藏文件
            exclude_args = [
                '-x!META-INF\\*',
                '-x!.*',
                '-x!__MACOSX\\*',
                '-x!_7z_file_list.txt'
            ]
            cmd.extend(exclude_args)

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=input_dir)
            if result.returncode != 0:
                raise ApkRepkgError(f"7z 压缩失败: {result.stderr}")

        finally:
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)

        print("[INFO] 7z 打包成功")

        if align:
            self._zipalign(output_apk)

        return output_apk

    def _zip_build_with_python(self, input_dir: str, output_apk: str, align: bool) -> str:
        """使用 Python zipfile 压缩（回退方案）"""
        print(f"[INFO] 正在打包 (ZIP方式): {input_dir}")
        print(f"[INFO] 压缩级别: {config.ZIP_COMPRESS_LEVEL}")

        # 需要以STORE方式存储的文件（不压缩）
        store_extensions = {
            '.dex', '.so', '.png', '.jpg', '.jpeg', '.gif', '.webp',
            '.mp3', '.mp4', '.ogg', '.arsc'
        }

        store_filenames = {
            'resources.arsc',
            'AndroidManifest.xml',
        }

        with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED, compresslevel=config.ZIP_COMPRESS_LEVEL) as zf:
            for root, dirs, files in os.walk(input_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__MACOSX']
                if 'META-INF' in dirs:
                    dirs.remove('META-INF')

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, input_dir)

                    ext = os.path.splitext(file)[1].lower()
                    filename = os.path.basename(file)

                    if ext in store_extensions or filename in store_filenames:
                        compress_type = zipfile.ZIP_STORED
                    else:
                        compress_type = zipfile.ZIP_DEFLATED

                    zf.write(file_path, arcname, compress_type=compress_type)

        print("[INFO] ZIP打包成功")

        if align:
            self._zipalign(output_apk)

        return output_apk

    def aar_to_dex(self, aar_path: str, output_dex: str, output_dir: str = None) -> str:
        """
        将 AAR 包转换为 DEX 文件

        流程: AAR → 解压提取 classes.jar → d8 转换 → classes.dex

        Args:
            aar_path: AAR 文件路径
            output_dex: 输出 DEX 文件路径
            output_dir: 临时工作目录（默认使用系统临时目录）

        Returns:
            转换后的 DEX 文件路径
        """
        import tempfile

        aar_path = os.path.abspath(aar_path)
        output_dex = os.path.abspath(output_dex)

        if not os.path.isfile(aar_path):
            raise ApkRepkgError(f"AAR 文件不存在: {aar_path}")

        if not aar_path.lower().endswith('.aar'):
            raise ApkRepkgError(f"输入文件不是 AAR 格式: {aar_path}")

        print(f"[INFO] 正在转换 AAR → DEX")
        print(f"[INFO] 输入 AAR: {aar_path}")
        print(f"[INFO] 输出 DEX: {output_dex}")

        # 创建临时工作目录
        temp_dir = output_dir or tempfile.mkdtemp(prefix="aar_to_dex_")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. 解压 AAR，提取 classes.jar
            print("[INFO] 步骤 1/3: 解压 AAR 提取 classes.jar")
            with zipfile.ZipFile(aar_path, 'r') as zf:
                if 'classes.jar' not in zf.namelist():
                    raise ApkRepkgError(f"AAR 文件中没有 classes.jar: {aar_path}")
                zf.extract('classes.jar', path=temp_dir)

            jar_path = os.path.join(temp_dir, 'classes.jar')

            # 2. 使用 d8 将 JAR 转为 DEX
            print("[INFO] 步骤 2/3: 使用 d8 将 JAR 转换为 DEX")

            d8_cmd = [
                'java', '-jar', self.apksigner_path.replace('apksigner.bat', '').replace('apksigner', '') + '../build-tools/34.0.0/lib/d8.jar'
                if os.name == 'nt' and not os.path.isfile(getattr(config, 'D8_PATH', 'd8'))
                else getattr(config, 'D8_PATH', 'd8'),
            ]

            # 如果是 .bat 文件，直接调用；否则需要 java -jar
            d8_path = getattr(config, 'D8_PATH', 'd8')
            if d8_path.endswith('.bat') or d8_path.endswith('.exe'):
                d8_cmd = [d8_path]
            else:
                d8_cmd = ['java', '-jar', d8_path]

            # 添加 android.jar 作为 boot classpath
            android_jar = getattr(config, 'ANDROID_JAR_PATH', None)
            if android_jar and os.path.isfile(android_jar):
                d8_cmd.extend(['--lib', android_jar])

            d8_cmd.extend([
                '--output', temp_dir,
                jar_path
            ])

            print(f"[INFO] d8 命令: {' '.join(d8_cmd)}")
            result = subprocess.run(d8_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise ApkRepkgError(f"d8 转换失败: {result.stderr}")

            # 3. 移动 DEX 文件到目标位置
            print("[INFO] 步骤 3/3: 移动 DEX 文件")
            dex_source = os.path.join(temp_dir, 'classes.dex')

            if not os.path.isfile(dex_source):
                # d8 可能生成 classes-1.dex, classes-2.dex 等（多 DEX）
                dex_files = [f for f in os.listdir(temp_dir) if f.endswith('.dex')]
                if not dex_files:
                    raise ApkRepkgError(f"d8 未生成 DEX 文件，输出目录: {temp_dir}")
                dex_source = os.path.join(temp_dir, dex_files[0])

            # 如果目标目录不存在，创建它
            os.makedirs(os.path.dirname(output_dex), exist_ok=True)

            # 删除已存在的目标文件
            if os.path.exists(output_dex):
                os.remove(output_dex)

            shutil.move(dex_source, output_dex)

            print("[INFO] AAR → DEX 转换成功")
            return output_dex

        finally:
            # 清理临时文件（仅当使用系统临时目录时）
            if output_dir is None:
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"[INFO] 清理临时目录失败: {e}")

    def jar_to_dex(self, jar_path: str, output_dex: str, output_dir: str = None) -> str:
        """
        将 JAR 文件转换为 DEX 文件

        Args:
            jar_path: JAR 文件路径
            output_dex: 输出 DEX 文件路径
            output_dir: 临时工作目录（默认使用系统临时目录）

        Returns:
            转换后的 DEX 文件路径
        """
        import tempfile

        jar_path = os.path.abspath(jar_path)
        output_dex = os.path.abspath(output_dex)

        if not os.path.isfile(jar_path):
            raise ApkRepkgError(f"JAR 文件不存在: {jar_path}")

        if not jar_path.lower().endswith('.jar'):
            raise ApkRepkgError(f"输入文件不是 JAR 格式: {jar_path}")

        print(f"[INFO] 正在转换 JAR → DEX")
        print(f"[INFO] 输入 JAR: {jar_path}")
        print(f"[INFO] 输出 DEX: {output_dex}")

        # 创建临时工作目录
        temp_dir = output_dir or tempfile.mkdtemp(prefix="jar_to_dex_")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 使用 d8 将 JAR 转为 DEX
            print("[INFO] 使用 d8 将 JAR 转换为 DEX")

            d8_path = getattr(config, 'D8_PATH', 'd8')
            if d8_path.endswith('.bat') or d8_path.endswith('.exe'):
                d8_cmd = [d8_path]
            else:
                d8_cmd = ['java', '-jar', d8_path]

            # 添加 android.jar 作为 boot classpath
            android_jar = getattr(config, 'ANDROID_JAR_PATH', None)
            if android_jar and os.path.isfile(android_jar):
                d8_cmd.extend(['--lib', android_jar])

            d8_cmd.extend([
                '--output', temp_dir,
                jar_path
            ])

            print(f"[INFO] d8 命令: {' '.join(d8_cmd)}")
            result = subprocess.run(d8_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise ApkRepkgError(f"d8 转换失败: {result.stderr}")

            # 移动 DEX 文件到目标位置
            dex_source = os.path.join(temp_dir, 'classes.dex')

            if not os.path.isfile(dex_source):
                # 检查多 DEX 文件
                dex_files = [f for f in os.listdir(temp_dir) if f.endswith('.dex')]
                if not dex_files:
                    raise ApkRepkgError(f"d8 未生成 DEX 文件，输出目录: {temp_dir}")
                dex_source = os.path.join(temp_dir, dex_files[0])

            os.makedirs(os.path.dirname(output_dex), exist_ok=True)

            if os.path.exists(output_dex):
                os.remove(output_dex)

            shutil.move(dex_source, output_dex)

            print("[INFO] JAR → DEX 转换成功")
            return output_dex

        finally:
            if output_dir is None:
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"[INFO] 清理临时目录失败: {e}")

    def _zipalign(self, apk_path: str) -> None:
        """
        对APK进行zipalign对齐优化

        Args:
            apk_path: APK文件路径（原地修改）
        """
        if not os.path.isfile(self.zipalign_path):
            print(f"[INFO] zipalign 不可用，跳过对齐优化: {self.zipalign_path}")
            return

        print(f"[INFO] 正在进行zipalign对齐优化...")

        # 创建临时文件
        temp_apk = apk_path + ".aligned"

        try:
            cmd = [self.zipalign_path, "-f", "4", apk_path, temp_apk]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"[INFO] zipalign 失败，跳过: {result.stderr}")
                return

            # 替换原文件
            shutil.move(temp_apk, apk_path)
            print("[INFO] zipalign 对齐完成")

        except FileNotFoundError:
            print(f"[INFO] zipalign 不可用，跳过对齐优化")
        except Exception as e:
            print(f"[INFO] zipalign 处理失败: {e}")
            if os.path.exists(temp_apk):
                os.remove(temp_apk)

    def sign(self, apk_path: str, keystore_path: str,
             storepass: str, alias: str, keypass: Optional[str] = None,
             v1_only: bool = False, v2_only: bool = False) -> str:
        """
        签名APK文件

        Args:
            apk_path: 未签名的APK文件路径
            keystore_path: 密钥库文件路径
            storepass: 密钥库密码
            alias: 密钥别名
            keypass: 密钥密码（默认与storepass相同）
            v1_only: 仅使用V1签名（JAR签名，兼容性好但体积大）
            v2_only: 仅使用V2签名（APK签名，体积小，Android 7.0+）

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

        # 确定签名方式（优先使用参数，否则使用config配置）
        sign_mode = getattr(config, 'SIGN_MODE', 'V1_V2')

        if v1_only:
            v1_enabled, v2_enabled = "true", "false"
            print("[INFO] 使用 V1 签名 (JAR签名)")
        elif v2_only:
            v1_enabled, v2_enabled = "false", "true"
            print("[INFO] 使用 V2 签名 (APK签名，体积更小)")
        elif sign_mode == "V1_ONLY":
            v1_enabled, v2_enabled = "true", "false"
            print("[INFO] 使用 V1 签名 (JAR签名) [配置]")
        elif sign_mode == "V2_ONLY":
            v1_enabled, v2_enabled = "false", "true"
            print("[INFO] 使用 V2 签名 (APK签名，体积更小) [配置]")
        else:  # V1_V2
            v1_enabled, v2_enabled = "true", "true"
            print("[INFO] 使用 V1+V2 签名 [配置]")

        # 尝试使用 apksigner（优先），否则使用 jarsigner
        apksigner_cmd = [
            self.apksigner_path,
            "sign",
            "--ks", keystore_path,
            "--ks-pass", f"pass:{storepass}",
            "--ks-key-alias", alias,
            "--key-pass", f"pass:{keypass}",
            "--v1-signing-enabled", v1_enabled,
            "--v2-signing-enabled", v2_enabled,
            apk_path
        ]

        try:
            result = subprocess.run(apksigner_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise ApkRepkgError(f"apksigner 签名失败: {result.stderr}")
        except FileNotFoundError:
            # apksigner 不可用，回退到 jarsigner
            print("[INFO] apksigner 不可用，使用 jarsigner...")
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

        # 打印签名输出以便调试
        if result.stdout:
            print(result.stdout[:500])  # 只打印前500字符

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

    def repack_zip(self, input_dir: str, output_apk: str,
                   keystore_path: str = None, storepass: str = None,
                   alias: str = None, align: bool = None) -> str:
        """
        ZIP方式重打包流程：ZIP打包 -> zipalign -> 签名

        直接从解压目录重新压缩并签名，不使用apktool。
        适用于添加DEX文件、修改资源后的快速重打包。

        Args:
            input_dir: 解压后的APK目录路径
            output_apk: 输出APK路径
            keystore_path: 密钥库文件路径，默认使用config.py配置
            storepass: 密钥库密码，默认使用config.py配置
            alias: 密钥别名，默认使用config.py配置
            align: 是否进行zipalign对齐优化，默认使用config.py配置

        Returns:
            重打包并签名后的APK文件路径
        """
        # 使用配置文件默认值
        keystore_path = keystore_path or config.DEFAULT_KEYSTORE
        storepass = storepass or config.DEFAULT_STOREPASS
        alias = alias or config.DEFAULT_ALIAS
        align = align if align is not None else getattr(config, 'ZIPALIGN_ENABLED', True)

        print("=" * 50)
        print("APK ZIP方式重打包工具")
        print("=" * 50)

        # 1. ZIP打包
        print("\n[步骤 1/2] ZIP打包")
        print("-" * 50)
        built_apk = self.zip_build(input_dir, output_apk, align=align)

        # 2. 签名（使用config.py中的SIGN_MODE配置）
        print("\n[步骤 2/2] 签名 APK")
        print("-" * 50)
        final_apk = self.sign(built_apk, keystore_path, storepass, alias)

        print("\n" + "=" * 50)
        print("ZIP方式重打包完成！")
        print(f"输出文件: {final_apk}")
        print("=" * 50)

        return final_apk


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="APK自动重打包工具 - 基于apktool或ZIP方式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # apktool方式打包
  python apk_repackager.py build -i decoded/ -o app.apk

  # 签名
  python apk_repackager.py sign -i app.apk

  # apktool方式完整流程（打包+签名）
  python apk_repackager.py repack -i decoded/ -o app.apk

  # ZIP方式完整流程（直接压缩+签名，适用于添加DEX）
  python apk_repackager.py repack-zip -i extracted/ -o app.apk

  # ZIP方式打包（不签名）
  python apk_repackager.py zip-build -i extracted/ -o app.apk

  # AAR转DEX
  python apk_repackager.py aar-to-dex -i library.aar -o classes.dex

  # JAR转DEX
  python apk_repackager.py jar-to-dex -i classes.jar -o classes.dex
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

    # zip-build命令
    zip_build_parser = subparsers.add_parser("zip-build", help="ZIP方式打包（直接压缩，不使用apktool）")
    zip_build_parser.add_argument("-i", "--input", required=True, help="解压后的APK目录路径")
    zip_build_parser.add_argument("-o", "--output", required=True, help="输出APK路径")
    zip_build_parser.add_argument("--no-align", action="store_true", help="跳过zipalign对齐优化")

    # repack-zip命令
    repack_zip_parser = subparsers.add_parser("repack-zip", help="ZIP方式完整流程（压缩+签名，适用于添加DEX文件）")
    repack_zip_parser.add_argument("-i", "--input", required=True, help="解压后的APK目录路径")
    repack_zip_parser.add_argument("-o", "--output", required=True, help="输出APK路径")
    repack_zip_parser.add_argument("-k", "--keystore", default=config.DEFAULT_KEYSTORE, help=f"密钥库路径 (默认: {config.DEFAULT_KEYSTORE})")
    repack_zip_parser.add_argument("-p", "--storepass", default=config.DEFAULT_STOREPASS, help="密钥库密码")
    repack_zip_parser.add_argument("-a", "--alias", default=config.DEFAULT_ALIAS, help=f"密钥别名 (默认: {config.DEFAULT_ALIAS})")
    repack_zip_parser.add_argument("--no-align", action="store_true", help="跳过zipalign对齐优化")

    # aar-to-dex命令
    aar_to_dex_parser = subparsers.add_parser("aar-to-dex", help="将AAR包转换为DEX文件")
    aar_to_dex_parser.add_argument("-i", "--input", required=True, help="输入AAR文件路径")
    aar_to_dex_parser.add_argument("-o", "--output", required=True, help="输出DEX文件路径")

    # jar-to-dex命令
    jar_to_dex_parser = subparsers.add_parser("jar-to-dex", help="将JAR文件转换为DEX文件")
    jar_to_dex_parser.add_argument("-i", "--input", required=True, help="输入JAR文件路径")
    jar_to_dex_parser.add_argument("-o", "--output", required=True, help="输出DEX文件路径")

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

        elif args.command == "zip-build":
            repkg = ApkRepkg()
            align = not getattr(args, 'no_align', False)
            output = repkg.zip_build(args.input, args.output, align=align)
            print(f"\n输出: {output}")

        elif args.command == "repack-zip":
            repkg = ApkRepkg()
            align = not getattr(args, 'no_align', False)
            output = repkg.repack_zip(args.input, args.output, args.keystore, args.storepass, args.alias, align=align)
            print(f"\n输出: {output}")

        elif args.command == "aar-to-dex":
            repkg = ApkRepkg()
            output = repkg.aar_to_dex(args.input, args.output)
            print(f"\n输出: {output}")

        elif args.command == "jar-to-dex":
            repkg = ApkRepkg()
            output = repkg.jar_to_dex(args.input, args.output)
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
        print("=" * 50)
        print("APK 重打包工具 - PyCharm 运行模式")
        print("=" * 50)
        print(f"输入目录: {config.INPUT_DIR}")
        print(f"输出APK:  {config.OUTPUT_APK}")
        print(f"密钥库:   {config.DEFAULT_KEYSTORE}")
        print("=" * 50)
        print("\n请选择操作模式:")
        print("  1. apktool 方式 (repack) - 反编译目录 → apktool重建 → 签名")
        print("  2. ZIP 方式 (repack-zip)  - 解压目录 → 直接压缩 → 签名")
        print("\n输入选择 (1 或 2，默认 1): ", end="")

        try:
            choice = input().strip()

            if choice == "2":
                print("\n[模式] ZIP 方式重打包")
                print("-" * 50)
                repkg = ApkRepkg()
                repkg.repack_zip(
                    input_dir=config.INPUT_DIR,
                    output_apk=config.OUTPUT_APK
                )
            else:
                print("\n[模式] apktool 方式重打包")
                print("-" * 50)
                repkg = ApkRepkg()
                repkg.repack(
                    input_dir=config.INPUT_DIR,
                    output_apk=config.OUTPUT_APK
                )

        except Exception as e:
            print(f"\n[错误] {e}")
            import traceback
            traceback.print_exc()
            input("\n按回车键退出...")
    else:
        # 命令行模式
        sys.exit(main())

