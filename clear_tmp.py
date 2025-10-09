import os
import tempfile
import shutil


def clear_tmp():
    tmp_dir = tempfile.gettempdir()  # 通常は "/tmp"
    print(f"Clearing temporary directory: {tmp_dir}")

    # /tmp 以下の全ファイル・フォルダを削除
    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # ファイル or シンボリックリンク削除
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # ディレクトリ削除
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")
            return f"Failed to delete {file_path}: {e}"

    print("✅ /tmp directory cleared.")
    return "✅ /tmp directory cleared."

