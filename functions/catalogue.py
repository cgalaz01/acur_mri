import os
import re
import shutil

from typing import Any, Dict, List, Union
from pathlib import Path

import pandas as pd
import numpy as np
import png

import pydicom

import matplotlib.pyplot as plt

from functions.cataloguing.group import Categories
from functions.cataloguing.split import MetadataSplit


_dicom_tags = ['MRAcquisitionType', 'SliceThickness', 'RepetitionTime', 'EchoTime',
               'NumberOfAverages', 'SpacingBetweenSlices', 'EchoTrainLength',
               'FlipAngle', 'PixelSpacing', 'AcquisitionMatrix', 'Rows', 'Columns',
               'MagneticFieldStrength']


def sequence_count() -> pd.DataFrame:
    df = pd.read_csv('patient_sequences.csv')
    df = df.drop(columns=['Dataset'])
    data = np.asarray(df.sum())
    
    data = {'Sequence': df.columns, 'Count': data}
    df = pd.DataFrame.from_dict(data)
    df.sort_values(by=['Count'], inplace=True, ascending=False)
    
    return df
    

def __dicom_to_png(input_path, output_path, output_filename):
    os.makedirs(output_path, exist_ok=True)
    all_files = os.listdir(input_path)
    middle_index = int(len(all_files) / 2)
    filename = os.listdir(input_path)[middle_index]
    dicom_file = pydicom.dcmread(os.path.join(input_path, filename))
    
    shape = dicom_file.pixel_array.shape

    # Convert to float to avoid overflow or underflow losses.
    image_2d = dicom_file.pixel_array.astype(float)
    
    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
    
    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)
    
    # Write the PNG file
    with open(os.path.join(output_path, output_filename), 'wb') as png_file:
        w = png.Writer(shape[1], shape[0], greyscale=True)
        w.write(png_file, image_2d_scaled)
    

def __get_tag_info(directory: Union[str, Path]) -> Dict[str, Any]:
    filename = os.listdir(directory)[0]
    dataset = pydicom.dcmread(os.path.join(directory, filename))
    
    tags = {}
    for tag_key in _dicom_tags:
        try:
            tags[tag_key] = dataset.data_element(tag_key).value
        except:
            tags[tag_key] = None
        
    if tags['SpacingBetweenSlices'] is None:
        tags['SpacingBetweenSlices'] = tags['SliceThickness']
    
    return tags
    
    
def __add_unique_tag_info(tag_dict: Dict[str, List[Dict]], entry_key: str,
                          entry_values: Dict) -> None:
    
    if entry_key in tag_dict:
        add_entry  = True
        for value in tag_dict[entry_key]:
            if entry_values == value:
                add_entry = False
                break
        if add_entry:
            tag_dict[entry_key].append(entry_values)
    else:
        tag_dict[entry_key] = [entry_values]


def __expand_tags(entry_values: Dict) -> Dict:
    expanded_values = {}

    for tag_key in _dicom_tags:
        if tag_key == 'MRAcquisitionType':
            expanded_values[tag_key] = re.findall(r'\d+', entry_values[tag_key])[0]
        elif tag_key == 'PixelSpacing':
            new_key = tag_key + 'Row'
            expanded_values[new_key] = entry_values[tag_key][0]
            new_key = tag_key + 'Column'
            expanded_values[new_key] = entry_values[tag_key][1]
        elif tag_key == 'AcquisitionMatrix':
            row = entry_values['AcquisitionMatrix'][0] if entry_values['AcquisitionMatrix'][0] != 0 else entry_values['AcquisitionMatrix'][2]
            column = entry_values['AcquisitionMatrix'][1] if entry_values['AcquisitionMatrix'][1] != 0 else entry_values['AcquisitionMatrix'][3]
            pixel_size_row = entry_values['Rows'] * entry_values['PixelSpacing'][0] / row
            pixel_size_column = entry_values['Columns'] * entry_values['PixelSpacing'][1] / column
            
            expanded_values['PixelSizeRow'] = pixel_size_row            
            expanded_values['PixelSizeColumn'] = pixel_size_column
        elif tag_key == 'Rows' or tag_key == 'Columns':
            continue
        else:
            expanded_values[tag_key] = entry_values[tag_key]
        
    return expanded_values


def __add_tag_info(tag_dict: Dict[str, Dict[str, List]], entry_key: str,
                   entry_values: Dict) -> None:
    # Sequence: <tag key: List[values] >
    
    expanded_entry_values = __expand_tags(entry_values)
    #print(tag_dict)
    if entry_key in tag_dict:
        for tag in tag_dict[entry_key]:
            #print(expanded_entry_values[tag])
            if expanded_entry_values[tag] is None:
                continue
            tag_dict[entry_key][tag].append(expanded_entry_values[tag])
    else:
        tag_dict[entry_key] = {}
        for tag in expanded_entry_values:
            if expanded_entry_values[tag] is None:
                tag_dict[entry_key][tag] = []
            else:
                tag_dict[entry_key][tag] = [expanded_entry_values[tag]]


def __tags_to_dataframe(tag_dict: Dict[str, List[Dict]]) -> pd.DataFrame:
    columns = _dicom_tags.copy()
    columns.insert(0, 'SequenceDescription')
    columns.insert(1, 'Variant')
    
    df = pd.DataFrame(columns=columns) 
    
    for sequence, tags_info in tag_dict.items():
        variant = 1
        for tag_info in tags_info:
            row = tag_info.copy()
            row['SequenceDescription'] = sequence
            row['Variant'] = variant
            df = df.append(row, ignore_index=True)
            variant += 1
            
    return df


def __plot_histograms(tag_dict: Dict[str, Dict[str, List]], group: str) -> None:
    path = 'catalogue_output/histograms/' + group
    os.makedirs(path, exist_ok=True)
    
    for sequence in tag_dict:
        fig = plt.figure(figsize=(10, 20))
        plot_index = 1
        
        for tag in tag_dict[sequence]:
            plt.subplot(5, 3, plot_index)
            plt.hist(tag_dict[sequence][tag], bins=10)
            plt.title(tag)
            
            plot_index += 1

        plt.suptitle(sequence, fontsize=20)
        fig.savefig(os.path.join(path, sequence + '.png'), bbox_inches='tight')
        plt.close(fig)


def __plot_scatter_plots(tag_dict: Dict[str, Dict[str, List]], group: str) -> None:
    path = 'catalogue_output/scatter_plots/' + group
    os.makedirs(path, exist_ok=True)
    
    for sequence in tag_dict:
        fig = plt.figure()
        
        plt.title('Repetition/Echo Time - ' + sequence)
        plt.scatter(tag_dict[sequence]['RepetitionTime'], tag_dict[sequence]['EchoTime'])
        plt.xlabel('Repetition Time (ms)')
        plt.ylabel('Echo Time (ms)')
        plt.grid()
        
        fig.savefig(os.path.join(path, sequence + '.png'), bbox_inches='tight')
        plt.close(fig)
    
        
def overview(directory: Union[str, Path]) -> None:
    current_sequence = None
    categories = Categories()
    metadata_split = MetadataSplit()
    
    cine_data = {}
    
    data_count = {}
    
    # Per patient
    for folder_name in next(os.walk(directory))[1]:
        print('Reading patient folder: ' + folder_name)
        cine_sequences = []
        multi_sequences = []
        # Per sequence
        
        already_added_for_patient = {}
        for subfolder_name in next(os.walk(os.path.join(directory, folder_name)))[1]:
            # Folder naming is expected to have the format: Series<number>_<series_description>
            series, sequence = subfolder_name.split('_', 1)
            #if sequence == current_sequence:
            #    continue
            
            current_sequence = sequence
            
            sequence_mapping = Categories.get_label(sequence)
            categories.store_sequence_mapping(sequence, sequence_mapping['type'], sequence_mapping['anatomy'])
            
            #metadata = metadata_split.get_tag_info(os.path.join(directory, folder_name, subfolder_name))
            #_ = metadata_split.get_split_id(sequence_mapping['type'], sequence_mapping['anatomy'], metadata)
            print(sequence_mapping)
            if sequence_mapping['anatomy']:
                new_folder_name = series + '_' + sequence_mapping['type'] + '_' + sequence_mapping['anatomy']
            else:
                new_folder_name = series + '_' + sequence_mapping['type'] + '_Other'
                
            if Categories.is_repeat(sequence):
                new_folder_name += '_repeat'
                continue
            
            if new_folder_name in already_added_for_patient:
                continue
            
            multi_sequences.append(sequence_mapping)
            
            already_added_for_patient[new_folder_name] = 1
            
            if new_folder_name in data_count:
                data_count[new_folder_name] += 1
            else:
                data_count[new_folder_name] = 1
 
            try:
                os.rename(os.path.join(directory, folder_name, subfolder_name),
                          os.path.join(directory, folder_name, new_folder_name))
            except FileExistsError:
                while True:
                    duplicate_index = 1
                    new_folder_name_duplicate = new_folder_name + '_' + str(duplicate_index)
                    
                    try:
                        os.rename(os.path.join(directory, folder_name, subfolder_name),
                                  os.path.join(directory, folder_name, new_folder_name_duplicate))
                    except FileExistsError:
                        duplicate_index += 1
                        continue
                    
                    break

            
    