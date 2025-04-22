import os
import sys
import subprocess
from pathlib import Path

def compile_protos():
    """編譯所有 proto 文件"""
    current_dir = Path(__file__).parent.resolve()

    # 編譯 robot.proto
    robot_proto = current_dir / "robot" / "robot.proto"
    output_dir = current_dir / "robot"  # 輸出到 app/protos/robot 目錄內

    os.makedirs(output_dir, exist_ok=True)

    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{current_dir / 'robot'}",            # proto 的 import root 指定為 robot/
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(robot_proto)
    ], check=True)

    print("Proto 文件編譯完成")

if __name__ == "__main__":
    compile_protos()
