import os
import sys
import subprocess
from pathlib import Path

def compile_protos():
    """すべての proto ファイルをコンパイル"""
    current_dir = Path(__file__).parent.resolve()

    # robot.proto をコンパイル
    robot_proto = current_dir / "robot" / "robot.proto"
    output_dir = current_dir / "robot"  # app/protos/robot ディレクトリ内に出力

    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{current_dir / 'robot'}",            # proto の import root を robot/ に指定
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(robot_proto)
    ], check=True)

    print("Proto ファイルのコンパイルが完了しました")

if __name__ == "__main__":
    compile_protos()