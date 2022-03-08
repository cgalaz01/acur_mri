"""
====================
Anonymize DICOM data
====================

"""

import os
import shutil
import json

from functools import wraps
from typing import Any, Dict, List, Tuple, Union
from pathlib import Path

import pydicom


class Anonymisation():

    __patient_name_key = 'PatientName'
    __patient_id_key = 'PatientID'    
    __index_key = 'PatientIndex'
    __accession_key = 'AccessionNumber'
    __study_date_key = 'StudyDate'
    __new_patient_name_key = 'NewPatientName'
    __folder_key = 'OriginalBaseFolder'
    
    __replace_tags = {'PatientBirthDate': '00010101',
                      'PatientID': 'anonymised',
                      'PatientAddress': 'anonymised',
                      'ReferringPhysicianName': 'anonymised'}
    
    __delete_tags = ['OtherPatientIDs',
                     'OtherPatientNames',
                     'OtherPatientIDsSequence',
                     'IssuerOfPatientID',
                     'InstitutionName',
                     'InstitutionAddress',
                     'PerformingPhysicianName',
                     'PerformingPhysicianIdentificationSequence',
                     'OperatorsName',
                     'OperatorIdentificationSequence',
                     'IssuerOfPatientID',
                     'IssuerOfPatientIDQualifiersSequence',
                     'ReferencedPatientPhotoSequence',
                     'ResponsiblePerson',
                     'ResponsiblePersonRole',
                     'ResponsibleOrganization',
                     'ReferringPhysicianIdentificationSequence',
                     'ConsultingPhysicianIdentificationSequence',
                     'PhysiciansOfRecord',
                     'PhysiciansOfRecordIdentificationSequence',
                     'NameOfPhysiciansReadingStudy',
                     'PhysiciansReadingStudyIdentificationSequence',
                     'PatientComments',
                     'InstitutionalDepartmentName']
    
    
    def __init__(self, json_directory: Union[str, Path],
                 source_directory: Union[str, Path],
                 target_directory: Union[str, Path],
                 verbose=0) -> None:
        
        self.json_directory = Path(json_directory)
        self.source_directory = Path(source_directory)
        self.target_directory = Path(target_directory)
        
        self.mapping = {}
        self.load_json_mapping()
    
        self.verbose = verbose
    
    
    @staticmethod
    def retry_function(times: int, function):
        """
        A wrapper function that will execute a given function upto 'times' in case
        an exception was thrown. This is to be used to overcome network instabilities
        when reading/writing files.

        Parameters
        ----------
        times : int
            The number of times to try executing a function in case an exception
            was thrown.
        function : TYPE
            Function to execute multiple times in case of exception thrown.

        Raises
        ------
        Exception
            Raises original exception if all 'times' have failed with an exception.

        Returns
        -------
        TYPE
            Returns the results of the passed function.

        """
        @wraps(function)
        def try_function(*args, **kwargs):
            e = Exception('Retry Exception Failed.')
            for i in range(times):
                try:
                    return function(*args, **kwargs)
                except Exception as caught_exception:  
                    e = caught_exception
    
            raise e
    
        return try_function
    
    
    @staticmethod
    def listdir(directory: Union[str, Path]) -> List[str]:
        """
        Wrapper for os.listdir. Repeats listdir call to overcome network instabilities.

        Parameters
        ----------
        directory : Union[str, Path]
            Directory to root folder.

        Returns
        -------
        List[str]
            File list.

        """
        repeat_times = 20
        exception_repeat_times = 10
        max_size = -1
        selected_list = []
        
        for i in range(repeat_times):
            try:
                directory_list = Anonymisation.retry_function(exception_repeat_times, os.listdir)(directory)
                size = len(directory_list)
                if max_size < size:
                    max_size = size
                    selected_list = directory_list
            except:
                pass
            
        return selected_list
    
    
    @staticmethod
    def isdir(directory: Union[str, Path]) -> bool:
        """
        Wrapper for os.path.isdir. Repeats isdir call to overcome network instabilities.

        Parameters
        ----------
        directory : Union[str, Path]
            Path to directory.

        Returns
        -------
        bool
            True if given path is a directory.

        """
        repeat_times = 40
        value = False
        
        for i in range(repeat_times):
            value = value or os.path.isdir(directory)
            
        return value
    
    
    @staticmethod
    def isfile(directory: Union[str, Path]) -> bool:
        """
        Wrapper for os.path.isfile. Repeats isflie call to overcome network instabilities.

        Parameters
        ----------
        directory : Union[str, Path]
            Path to file.

        Returns
        -------
        bool
            True if given path is of a file.

        """
        repeat_times = 40
        value = False
        
        for i in range(repeat_times):
            value = value or os.path.isfile(directory)
            
        return value
        
        
    @staticmethod
    def patient_directory_yield(root_directory: Union[str, Path]) -> Path:
        """
        Generator of folder directories for the given root path. Expects the
        root directory to contain patient-level folders.

        Parameters
        ----------
        root_directory : Union[str, Path]
            The directory to the root folder to return all subfolders.

        Yields
        ------
        Path
            The full path to a subfolder in the given root directory.

        """
        for patient_folder in Anonymisation.listdir(root_directory):
            patient_directory = os.path.join(root_directory, patient_folder)
            if Anonymisation.isdir(patient_directory):
                yield Path(patient_directory)
        

    @staticmethod
    def sequence_directory_yield(patient_directory: Union[str, Path]) -> Path:
        """
        Generator of folder directories for the given patient path. Expects the
        root directory to contain folders with scan series for a specific patient.

        Parameters
        ----------
        patient_directory : Union[str, Path]
            The directory to the patient folder to return all subfolders.

        Yields
        ------
        Path
            The full path to a subfolder in the given patient directory.

        """
        for sequence_folder in Anonymisation.listdir(patient_directory):
            sequence_directory = os.path.join(patient_directory, sequence_folder)
            if Anonymisation.isdir(sequence_directory):
                yield Path(sequence_directory)         


    @staticmethod
    def dicom_directory_yield(sequence_directory: Union[str, Path]) -> Path:
        """
        Generator of DICOM file directories for the given dicom folder path.
        Expects the DICOM folder (patient scan series) to contain DICOM files.

        Parameters
        ----------
        sequence_directory : Union[str, Path]
            The directory to the DICOM folder to return all valid (extension '.dcm')
            files.

        Yields
        ------
        Path
            The full path to a DICOM file in the given DICOM (patient series)
            folder.

        """
        for dicom_file in Anonymisation.listdir(sequence_directory):
            dicom_directory = os.path.join(sequence_directory, dicom_file)
            if Anonymisation.isfile(dicom_directory) and dicom_file.endswith('.dcm'):
                yield dicom_directory


    def save_json_mapping(self) -> None:
        """
        Saves as a json format the mapping between the original and the anonymised
        metadata. Stored information is also required to guarantee that the same
        patients are given the same unique anonymised ID.

        Returns
        -------
        None

        """
        os.makedirs(os.path.dirname(os.path.abspath(self.json_directory)), exist_ok=True)
        with open(self.json_directory, 'w') as fp:
            Anonymisation.retry_function(20, json.dump)(self.mapping, fp)
    
    
    def load_json_mapping(self) -> None:
        """
        Loads the json file that contains the mapping betwen the original and
        the anonymised metadata, if it exists. 

        Returns
        -------
        None

        """
        if Anonymisation.isfile(self.json_directory):
            with open(self.json_directory, 'r') as fp:
                self.mapping = Anonymisation.retry_function(20, json.load)(fp)
    

    def extract_key_info(self, dataset: pydicom.Dataset) -> Dict[str, Any]:
        """
        Retrieves key information from the DICOM tags:
            - Patient ID
            - Patient name
            - Accession number
            - Study date
            - Base folder name

        Parameters
        ----------
        dataset : pydicom.Dataset
            The DICOM dataset to extract information from.

        Returns
        -------
        Dict[str, Any]
            Returns a key-value pair of the patient metadata information.

        """
        patient_info = {}
        
        # Get patient id
        patient_id = dataset.data_element(self.__patient_id_key).value
        patient_info[self.__patient_id_key] = patient_id
        
        # Get patient name
        try:
            patient_name = dataset.data_element(self.__patient_name_key).value
        except:
            dataset.PatientName = 'Z^Z'
            patient_name = dataset.data_element(self.__patient_name_key).value
            
        patient_info[self.__patient_name_key] = patient_name
        
        # Get accession number
        accession_number = dataset.data_element(self.__accession_key).value
        patient_info[self.__accession_key] = accession_number
        
        # Get study date
        study_date = dataset.data_element(self.__study_date_key).value
        patient_info[self.__study_date_key] = study_date
        
        # Get the base folder of where the patient was original stored
        base_folder = os.path.basename(self.source_directory)
        patient_info[self.__folder_key] = base_folder
                
        return patient_info
        
        

    def exists_in_mapping(self, patient_info: Dict[str, Any]) -> bool:
        """
        Checks if the extracted key info already exists in the mapping between
        orginal and anonymised patient data. Uniqueness is based on the patient
        ID, accession number and study date.

        Parameters
        ----------
        patient_info : Dict[str, Any]
            The extracted key patient info as obtained from the extract_key_info()
            function.

        Returns
        -------
        bool
            Returns True if the the patient info exists in the mapping, false
            otherwise.

        """
        if patient_info[self.__patient_id_key] not in self.mapping:
            return False
        
        patient_values = self.mapping[patient_info[self.__patient_id_key]]

        accesion_study_list = zip(patient_values[self.__accession_key],
                                   patient_values[self.__study_date_key])

        for stored_accession_number, stored_study_date in accesion_study_list:
            if (stored_accession_number == patient_info[self.__accession_key] and
                stored_study_date == patient_info[self.__study_date_key]):
                return True
            
        return False

    
    def initialise_mapping_entry(self, patient_id: str) -> None:
        """
        Initialises the mapping entry for every new patient (based on the patient
        ID). Initialisation constists of creating deafult/empty values for all
        the keys

        Parameters
        ----------
        patient_id : str
            The patient ID, which is used as the key for the mapping between
            original and anonymised patient info.

        Returns
        -------
        None

        """
        if patient_id in self.mapping:
            return None
        
        self.mapping[patient_id] = {self.__index_key: None,
                                    self.__patient_name_key: [],
                                    self.__new_patient_name_key: [],
                                    self.__accession_key: [],
                                    self.__study_date_key: [],
                                    self.__folder_key: []}
        

    def get_patient_index(self, patient_info: Dict[str, Any]) -> int:
        """
        Returns the patient index based on the given patient info dictionary.

        Parameters
        ----------
        patient_info : Dict[str, Any]
            The key-value pair of the patient metadata information.

        Returns
        -------
        int
            Unique index for the given patient ID.

        """
        patient_id = patient_info[self.__patient_id_key]
        
        if self.mapping[patient_id][self.__index_key] is not None:
            return self.mapping[patient_id][self.__index_key]
        
        return len(self.mapping)


    @staticmethod
    def generate_new_patient_name(patient_name: pydicom.valuerep.PersonName,
                                  patient_index: int, study_date: int) -> str:
        """
        Generates a new anonymised patient name based on their initials, the
        passed uniquely generated index and the study date. 

        Parameters
        ----------
        patient_name : pydicom.valuerep.PersonName
            The non-anonymised patient name.
        patient_index : str
            The anonymised unique patient index.
        study_date : int
            The study date for the given patient dataset.

        Returns
        -------
        str
            The new anonymised patient name that uniquely identifies the patient.

        """
        try:
            new_patient_name = patient_name.given_name[0] + patient_name.family_name[0]
        except:
            new_patient_name = patient_name.family_name[0]
        return new_patient_name + str(patient_index) + '_' + str(study_date)
        

    def add_to_mapping(self, patient_info: Dict[str, Any]) -> str:
        """
        Adds the passed patient info dictionary to the mapping betwen the original
        and the anonymised data, if it doesn't already exist. Generates or returns
        respectively the anonymised index for the specific patient/metadata.

        Parameters
        ----------
        patient_info : Dict[str, Any]
            The key-value pair of the patient metadata information.

        Returns
        -------
        str
            Anonymised unique patient ID.

        """
        self.initialise_mapping_entry(patient_info[self.__patient_id_key])
        
        patient_id = patient_info[self.__patient_id_key]
        patient_index = self.get_patient_index(patient_info)
        patient_name = patient_info[self.__patient_name_key]
        study_date = patient_info[self.__study_date_key]
        accession_number = patient_info[self.__accession_key]
        folder_name = patient_info[self.__folder_key]
        new_patient_name = self.generate_new_patient_name(patient_name, patient_index, study_date)
        
        if self.exists_in_mapping(patient_info):
            return new_patient_name
        
        self.mapping[patient_id][self.__index_key] = patient_index
        self.mapping[patient_id][self.__patient_name_key].append(str(patient_name))
        self.mapping[patient_id][self.__new_patient_name_key].append(new_patient_name)
        self.mapping[patient_id][self.__study_date_key].append(study_date)
        self.mapping[patient_id][self.__accession_key].append(accession_number)
        self.mapping[patient_id][self.__folder_key].append(folder_name)
    
        return new_patient_name


    def anonymise_dicom(self, dataset: pydicom.Dataset) -> Tuple[pydicom.Dataset, str]:
        """
        Extracts all key information from the tags. This is followed by an
        anonymisation process to remove patient or sensitive information from
        the DICOM tags.

        Parameters
        ----------
        dataset : pydicom.Dataset
            The DICOM dataset to extract key information and anonymise.

        Returns
        -------
        dataset : pydicom.Dataset
            The anonymised DICOM file.
        new_patient_name : str
            The unique anonymised patient ID.

        """
        patient_info = self.extract_key_info(dataset)
        new_patient_name = self.add_to_mapping(patient_info)
        
        # Change patient name
        try:
            dataset.data_element(self.__patient_name_key).value = new_patient_name
        except:
            dataset.PatientName = new_patient_name
        
        # Replace sensitive tags
        for field, value in self.__replace_tags.items():
            try:
                dataset.data_element(field).value = value
            except:
                dataset.add_new(field, 'CS', value)
        
        # Remove optional sensitive tags
        for field in self.__delete_tags:
            if field in dataset:
                delattr(dataset, field)
        
        # Remove all private tags
        try:
            dataset.remove_private_tags()
        except:
            # Try deleting individually the private tags and skip over the
            # faulty case (incorrectly populated tag)
            for tag in list(dataset._dict):
                if tag.is_private:
                    try:
                        del dataset[tag]
                    except:
                        continue
        
        return dataset, new_patient_name
    
    
    def anonymise(self, compress: bool = False) -> None:
        """
        Anonymises all patient datasets in the root directory, as set during
        the class constructor. A json file is created to keep record of the link
        between the original and anonymised data. In addition, it is used for
        persistence across different executions of the anonymisation script
        and across different datasets.
        
        The anonymised DICOM datasets are compressed (zipped).

        Returns
        -------
        None

        """
        for patient_directory in self.patient_directory_yield(self.source_directory):
            if self.verbose == 1:
                print('Anonymising directory {}'.format(patient_directory))
            new_name = None
            for sequence_directory in self.sequence_directory_yield(patient_directory):
                sequence_name = os.path.basename(sequence_directory)
                
                for dicom_file in self.dicom_directory_yield(sequence_directory):
                    # Read and anonymise
                    dataset = Anonymisation.retry_function(50, pydicom.dcmread)(dicom_file, force=True)
                    dataset, new_name = self.anonymise_dicom(dataset)
                    # Save the anonymised DICOM file to target directory
                    os.makedirs(os.path.join(self.target_directory, new_name), exist_ok=True)
                    file_name = sequence_name + '_' + os.path.basename(dicom_file)
                    Anonymisation.retry_function(50, dataset.save_as)(os.path.join(self.target_directory, new_name, file_name))
            
            # Compress the anonymised patient directory
            if compress:
                shutil.make_archive(new_name, 'zip', os.path.join(self.target_directory, new_name),
                                    os.path.join(self.target_directory, new_name))
                shutil.rmtree(os.path.join(self.target_directory, new_name))
            
            self.save_json_mapping()


if __name__ == '__main__':
    dire = 'directory\\to\\data'
    newdire = 'directory\\to\\anonymised_data'
    
    anonymisation = Anonymisation('record_linkage.json', dire, newdire, verbose=1)
    anonymisation.anonymise()
