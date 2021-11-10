import os

from typing import List, Union
from pathlib import Path


def directory_folders(directory: Union[str, Path]) -> List[str]:
    """
    Returns the names of all top-level folders of the given directory.

    Parameters
    ----------
    directory : Union[str, Path]
        A string or Path object of the directory to obtain the folders for.

    Returns
    -------
    List[str]
        A list of strings of all the folder names found.

    """
    folder_list = [folder_name for folder_name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, folder_name))]
    
    return folder_list