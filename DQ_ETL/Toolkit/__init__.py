import sys
import pathlib

current_path = pathlib.Path(__file__).resolve()
project_root = current_path.parent.parent
sys.path.append(str(project_root))