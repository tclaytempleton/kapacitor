import os


def build_paths(basepaths):
    """
    Args:
        basepaths: a list of strings; directories and files

    Returns: a list of strings; files in directories (to depth of 1) + files
    """
    paths = []
    for basepath in basepaths:
        if os.path.isfile(basepath):
            paths.append(basepath)
        else:
            paths.extend([os.path.join(basepath, f) for f in os.listdir(basepath) if os.path.isfile(os.path.join(basepath, f))])
    return paths
