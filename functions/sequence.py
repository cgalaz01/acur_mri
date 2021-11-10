import os
import csv

import pandas as pd

from typing import Dict, Union, Set
from pathlib import Path

from pivottablejs import pivot_ui


def get_descriptions(directory: Union[str, Path]) -> Set[str]:
    """
    Returns all unique sequence descriptions from all the patients from a given
    sorted directory. The description is extracted from the folder name and is
    expected to be formated as 'Series<number>_<sequence_description>'.

    Parameters
    ----------
    directory : Union[str, Path]
        The directory to the sorted root folder. The expected format is as following:
            directory/<patient_folder>/<sequence_folder>/<dicom_files>

    Returns
    -------
    Set[str]
        All unique sequence descriptions found as a set object.

    """
    unique_descriptions = set()
    for folder_name in next(os.walk(directory))[1]:
        for subfolder_name in next(os.walk(os.path.join(directory, folder_name)))[1]:
            # Folder naming is expected to have the format: Series<number>_<series_description>
            series_description = subfolder_name.split('_', 1)[1]
            unique_descriptions.add(series_description)
    
    return unique_descriptions
    

def create_csv_descriptions(descriptions: Set[str]) -> None:
    """
    Stores the given descriptions to a csv file, 'sequence_descriptors.csv'. It
    contains two columns, 'Origainal Label' which consits of the passed
    descriptions and 'Rename Label' which is left empty. The 'Rename Label'
    is used for the function rename_descriptors()

    Parameters
    ----------
    descriptions : Set[str]
        A set of the sequence labels.

    Returns
    -------
    None

    """
    list_descriptions = list(descriptions)
    list_descriptions.sort()
    
    header_labels = ['Original Label', 'Rename Label']
     
    filename = 'sequence_descriptors.csv'
        
    # writing to csv file
    with open(filename, 'w', newline='') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
            
        # writing the fields  
        csvwriter.writerow(header_labels)
            
        # writing the data rows
        for row in list_descriptions:
            csvwriter.writerows([[row]])
    

def read_csv_descriptor_renaming() -> Dict[str, str]:
    """
    Reads the csv file, 'sequence_descriptors.csv', that contains the original
    sequence descripitons and the mapping to their new description (if any).

    Returns
    -------
    Dict[str, str]
        A dictionary containing keys as the original sequence description and
        as values the intended new description. For any descriptions that do not
        contain any renaming descriptions are not included in the dicitonary.

    """
    filename = 'sequence_descriptors.csv'
    rename_mapping = {}
    
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        _ = next(csv_reader)  # skip header
        
        for row in csv_reader:
            if row[1] != '':
                rename_mapping[row[0]] = row[1]
    
    return rename_mapping
    

def rename_descriptors(directory: Union[str, Path], rename: Dict[str, str]) -> None:
    """
    In-place operation renaming the the sorted folder sequences. The folders
    arer expected to have the format: 'Series<number>_<sequence_description>'.

    Parameters
    ----------
    directory : Union[str, Path]
        The directory to the sorted root folder. The expected format is as following:
            directory/<patient_folder>/<sequence_folder>/<dicom_files>
    rename : Dict[str, str]
        A string to string dictionary containing the mapping of original to
        renamed sequence description. If a key does not exist in the dictionary
        then it will not be altered.

    Returns
    -------
    None

    """
    for folder_name in next(os.walk(directory))[1]:
        for subfolder_name in next(os.walk(os.path.join(directory, folder_name)))[1]:
            # Folder naming is expected to have the format: Series<number>_<series_description>
            series, description = subfolder_name.split('_', 1)

            # Check if the series description needs to be renamed            
            if description in rename:
                new_folder_name = series + '_' + rename[description]
                root_directory = os.path.join(directory, folder_name)
                
                os.rename(os.path.join(root_directory, subfolder_name),
                          os.path.join(root_directory, new_folder_name))
    
    
def get_dataframe(directory: Union[str, Path]) -> pd.DataFrame:
    """
    Returns a DataFrame inidcating which sequence labels are available for each
    patient ID. Sequence descriptions marked with '0' for a patient indicates
    that it doesn't exist and with '1' when it does.

    Parameters
    ----------
    directory : Union[str, Path]
        The directory to the sorted root folder. The expected format is as following:
            directory/<patient_folder>/<sequence_folder>/<dicom_files>

    Returns
    -------
    df : DataFrame
        A DataFrame containing all the sequence labels for each patient ID.

    """
    descriptions = get_descriptions(directory)
    
    dataset_key = 'Dataset'
    column_labels = list(descriptions)
    column_labels.sort()
    column_labels.insert(0, dataset_key)

    df = pd.DataFrame(columns=column_labels)    
    
    for folder_name in next(os.walk(directory))[1]:
        row = dict.fromkeys(descriptions, 0)
        row[dataset_key] = folder_name
        for subfolder_name in next(os.walk(os.path.join(directory, folder_name)))[1]:
            # Folder naming is expected to have the format: Series<number>_<series_description>
            description = subfolder_name.split('_', 1)[1]
            row[description] = 1
            
        df = df.append(row, ignore_index=True)
        
    return df


def create_html_csv_table(directory: Union[str, Path]) -> None:
    """
    Creates a csv ('patient_sequences.csv') and an interactive HTML
    ('patient_sequences.html') table with the sequence descriptions for each
    patient ID. Sequence descriptions marked with '0' for a patient indicates
    that it doesn't exist and with '1' when it does.

    Parameters
    ----------
    directory : Union[str, Path]
        The directory to the sorted root folder. The expected format is as following:
            directory/<patient_folder>/<sequence_folder>/<dicom_files>

    Returns
    -------
    None

    """
    df = get_dataframe(directory)
    pivot_ui(df, outfile_path='patient_sequences.html')
    df.to_csv('patient_sequences.csv', index=False)

