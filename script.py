import argparse

from pathlib import Path

from functions import anonymise_mri, catalogue, dicom_sort, sequence

        
def parse_arguments() -> argparse.Namespace:
    """
    Defines all accepted arguments.

    Returns
    -------
    args : argparse.Namespace
        Values of the passed arguments.

    """
    parser = argparse.ArgumentParser(description='Script to prepare the data.' +
                                     'One flag should be given at a time.')
    
    parser.add_argument('-a', '--anonymise', action='store_true',
                        help='Anonymises patient information in DICOM files. ' +
                        'Requires source and target directories.')
    
    parser.add_argument('-s', '--sort', action='store_true', help='Sorts the DICOM ' +
                        'files into subfolders based on the sequence descriptions' +
                        ' per patient. Requires source and target directories.')
    
    parser.add_argument('-d', '--descriptions', action='store_true', help='Stores in a ' +
                        'csv file all the unique sequence descritipns found in the sorted ' + 
                        'directory. This file is used for the renaming process.' +
                        'Requires source directory.')
    
    parser.add_argument('-r', '--rename', action='store_true', help='Renames specified' +
                        ' sequences based on the csv file in the sorted directory.' +
                        ' Requires target directory.')
    
    parser.add_argument('-o', '--sequence-overview', action='store_true',
                        help='Generates a csv and HTML files with which sequence' +
                        'descriptions are available for each patient. Requires' +
                        ' source directory.')
    
    parser.add_argument('-v', '--validate', action='store_true', help='Validates' +
                        ' the files between the anonymised and sorted directory.' +
                        ' Requires source and target directories.')
    
    parser.add_argument('-c', '--catalogue', action='store_true',
                        help='Catalogues and visualises the sequqnce descriptors' +
                        ' for the data. Requires source directory.')
    
    parser.add_argument('--source', nargs='?', default='',
                        help='The source directory path (read-only).')
                        
    parser.add_argument('--target', nargs='?', default='',
                        help='The target directory path (create/modify).')
                        
    args = parser.parse_args()
    return args


def anonymise(source_directory: str, target_directory: str) -> None:
    """
    Executes DICOM anonymise function.

    Parameters
    ----------
    source_directory : str
        The directory containing the original DICOM files.
    target_directory : str
        The destination directory in which the anonymised DICOM files will be
        copied to.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'anonymise' operation.")
    if not target_directory:
        print("'target' is required for 'anonymise' operation.")
        
    anonymisation = anonymise_mri.Anonymisation('record_linkage.json',
                                                Path(source_directory),
                                                Path(target_directory))
    anonymisation.anonymise()
    

def sort(source_directory: str, target_directory: str) -> None:
    """
    Executes DICOM sort function.

    Parameters
    ----------
    source_directory : str
        The directory containing the unsorted DICOM files.
    target_directory : str
        The destination directory in which the sorted DICOM files will be
        copied to.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'sort' operation.")
    if not target_directory:
        print("'target' is required for 'sort' operation.")
    
    dicom_sort.sort(Path(source_directory), Path(target_directory))
    

def validate(source_directory: str, target_directory: str) -> None:
    """
    Executes sort validation function.

    Parameters
    ----------
    source_directory : str
        The directory containing the unsorted DICOM files.
    target_directory : str
        The directory containing the sorted DICOM files.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'validate' operation.")
    if not target_directory:
        print("'target' is required for 'validate' operation.")
        
    dicom_sort.validate(Path(source_directory), Path(target_directory))
    

def descriptions(source_directory: str) -> None:
    """
    Executes sequence descriptions functoin, storing results into a csv file.

    Parameters
    ----------
    source_directory : str
        The sorted direcotry.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'descriptions' operation.")
        
    unique_descriptions = sequence.get_descriptions(Path(source_directory))
    sequence.create_csv_descriptions(unique_descriptions)


def rename(target_directory: str) -> None:
    """
    Executes rename function.

    Parameters
    ----------
    target_directory : str
        The sorted directory.

    Returns
    -------
    None

    """
    if not target_directory:
        print("'target' is required for 'rename' operation.")
    
    sequence.rename_descriptors(Path(target_directory), None)
    
    
def sequence_overview(source_directory: str) -> None:
    """
    Executes patient sequence descriptions overview function.

    Parameters
    ----------
    source_directory : str
        The sorted directory.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'sequence_overview' operation.")
        
    sequence.create_html_csv_table(Path(source_directory))
    
    
def catalogue_overview(source_directory: str) -> None:
    """
    

    Parameters
    ----------
    source_directory : str
        DESCRIPTION.

    Returns
    -------
    None

    """
    if not source_directory:
        print("'source' is required for 'catalogue' operation.")
        
    catalogue.overview(source_directory)
    
    
if __name__ == '__main__':
    args = parse_arguments()
    
    if args.anonymise:
        anonymise(args.source.strip(), args.target.strip())
        print("Finished executing 'anonymise'.")
    elif args.sort:
        sort(args.source.strip(), args.target.strip())
        print("Finished executing 'sort'.")
    elif args.validate:
        validate(args.source.strip(), args.target.strip())
        print("Finished executing 'validate'.")
    elif args.descriptions:
        descriptions(args.source.strip())
        print("Finished executing 'descriptions'.")
    elif args.rename:
        rename(args.target.strip())
        print("Finished executing 'rename'.")
    elif args.sequence_overview:
        sequence_overview(args.source.strip())
        print("Finished executing 'sequence_overview'.")
    elif args.catalogue:
        catalogue_overview(args.source.strip())
        print("Finished executing 'catalogue'.")
    else:
        print('No flags passed. Terminating...')

