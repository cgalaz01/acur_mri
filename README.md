# Framework for Large-Scale Automatic Curation of Heterogeneous Cardiac MRI (ACUR MRI)

## Setup
ACUR MRI can be setup using Anaconda and its dependencies are listed in the file 'environment.yml':

    # Create environment
    conda env create --file=environment.yml

During setup of the Python packages there might be a conflict between pydicom and dicomsorter. A newer version of pydicom is need (>= 2.1.1) as critical bugs were fixed, but dicomsorter depends on an earlier version. However, force installing the latest pydicom packages would not affect the functionality of dicomsorter used for this application:

    # Manually installing pip requirements in your conda environment
    conda activate cardiac_data
    pip install dicomsorter
    pip install pydicom==2.1.1
    pip install pypng


## Execution

Each execution is dependent on the previous step.

**Data Anonymisation**
The anonymisation process removes all patient/doctor identifiable information from the DICOM files. The application expects a directory of DICOM files and a target destination. The files are anonymised, copied and compressed. In the root folder of the code, it can be executed using the following command:

    python script.py -a --source="path/to/source/directory" --target="path/to/target/directory"

In addition to anonymising the files, in the root directory a JSON file is also created, 'mapping.json'. This file maps the original files to the anonymised ones. For subsequent executions, this file should always be in the root directory so the application can correctly continue to group together scans from the same patient even if they are anonymised.

**DICOM Sorting**
For this step, the algorithm will decompress the anonymised DICOM files and sort them into subfolders based on their series number. In the root folder of the code, it can be executed using the following command:
 
    python script.py -s --source="path/to/anonymised/source/directory" --target="path/to/target/directory"
    
**Cataloguing**
The final step renames the subfolders so that they are consistent when querying based on the image type and anatomical location. The renamed folders will be formatted as following: Series<*series_number*>\_<*image_type*>\_<*anatomy*>. Renamed subfolders that contain 'Other' keyword indicates that the application was not able to recognise the type or it has not been mapped yet. In the root folder of the code, it can be executed using the following command:

    python script.py -c --source="path/to/anonymised/and/sorted/source/directory"

Folder renaming will be done in-place on the given source directory.