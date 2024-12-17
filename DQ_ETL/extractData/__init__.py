import sys
import pathlib

current_path = pathlib.Path(__file__)
parent_folder = current_path.parent.parent

sys.path.append(parent_folder.name)

