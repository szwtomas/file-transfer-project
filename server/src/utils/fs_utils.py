import os

# Returns true if path exists inside "../../fs_root" directory
def path_exists(path) -> bool:
    return os.path.exists(os.path.join(os.path.dirname(__file__), "../../fs_root", path))

def get_file_size(path) -> int:
    return os.path.getsize(os.path.join(os.path.dirname(__file__), "../../fs_root", path))