import os
import zipfile
import shutil

from typing import Union
from pathlib import Path


def sort(source_dir: Union[str, Path], target_dir: Union[str, Path]) -> None:
    """
    Sorts the DICOM files based on the sequence description per patient ID. Not
    an inplace operation. The files are copied over to the new target directory
    structured in subfolders. The input patient folders are expected to be
    compressed in a 'zip' format.
    
    Note:
        If the folder already exists in the target directory it will assume that
        sorting was already done for that specific case. This doesn't check the
        file integrity.

    Parameters
    ----------
    source_dir : Union[str, Path]
        A string or Path object of the root directory from where to read through
        the DICOM files. It only searches one level deep, with expected format:
        'root_path/<patient_folder(compressed)>/<dicom_files>'.
    target_dir : Union[str, Path]
        A string or Path object of the output directory of the sorted DICOM
        files.

    Returns
    -------
    None

    """
    os.makedirs(target_dir, exist_ok=True)
    
    for folder_name in next(os.walk(source_dir))[2]:
        if folder_name.startswith('.'):
            continue
        
        source_folder = os.path.join(source_dir, folder_name)
        
        new_folder_name = folder_name
        compressed = False
        if folder_name.endswith('.zip'):
            compressed = True
            new_folder_name = folder_name[:-4]
        target_folder = os.path.join(target_dir, new_folder_name)        
        
        if os.path.isdir(target_folder):
            print("Folder '" + new_folder_name + "' already exists. Skipping...")
            continue
        
        
        if compressed:
            target_zip_folder = os.path.join(target_dir, 'temp_' + new_folder_name)
            print('Unzipping folder to: ' + target_zip_folder)
            os.makedirs(target_zip_folder, exist_ok=True)
            
            with zipfile.ZipFile(source_folder , 'r') as zip_ref:
                zip_ref.extractall(target_zip_folder)
                
            source_folder = target_zip_folder
            
        
        print("Sorting '" + new_folder_name + "':")
        folder_st = '\"' + source_folder +  '\" ' + '\"' + target_folder +  '\"'        
        os.system('dicomsorter ' + folder_st + ' --path SeriesNumber --path AcquisitionNumber --path SeriesDescription') #--path SeriesNumber InstanceNumber SeriesDescription
        
        if compressed:
            print('\nRemoving temporary folder: ' + target_zip_folder)
            shutil.rmtree(target_zip_folder)


def validate(source_dir: Union[str, Path], target_dir: Union[str, Path]) -> None:
    """
    Checks the file number and the total file size between the given source
    and target directories. Any differences are reported to the standard output.

    Parameters
    ----------
    source_dir : Union[str, Path]
        A string os Path object of the anonymised root directory.
    target_dir : Union[str, Path]
        A string os Path object of the sorted root directory.

    Returns
    -------
    None

    """
    from functions.utilities import direcotry_folders
    
    source_folders = set(direcotry_folders(source_dir))
    target_folders = set(direcotry_folders(target_dir))
    
    # Check for missing patient folders
    missing_folders = source_folders - target_folders
    if missing_folders:
        print('These folders are in source but are missing from target directory: '
              + ', '.join(missing_folders) + '\n')
        
    excess_folders = target_folders - source_folders
    if excess_folders:
        print('These folders are in target but do not exist in source directory: '
              + ', '.join(excess_folders) + '\n')
    
    # Check the number of files under each patient folder
    scan_folders = source_folders.intersection(target_folders)

    # Compare the number of files and byte size in source against target    
    for folder in scan_folders:
        source_files_num = 0
        source_files_size = 0
        target_files_num = 0
        target_files_size = 0
        
        for file in os.listdir(os.path.join(source_dir, folder)):
            if file.endswith('.dcm'):
                source_files_num += 1
                source_files_size += os.path.getsize(os.path.join(source_dir, folder, file))
                
        for subfolder in next(os.walk(os.path.join(target_dir, folder)))[1]:
            for file in os.listdir(os.path.join(target_dir, folder, subfolder)):
                if file.endswith('.dcm'):
                    target_files_num += 1
                    target_files_size += os.path.getsize(os.path.join(target_dir, folder, subfolder, file))
                                                      
                
        if source_files_num != target_files_num or source_files_size != target_files_size:
            print(('Mismatch files between source and target for patient {}: \
                   \nSource files: Number: {}, Size (bytes): {}\nTarget files: Number: {}, Size (bytes): {}\n')
                  .format(folder, source_files_num, source_files_size, target_files_num, target_files_size))
        

if __name__ == '__main__':
    source_directory = 'directory\\to\\compressed\\data'
    target_directory = 'directory\\to\\target\\sorted_data'
    
    sort(Path(source_directory), Path(target_directory))