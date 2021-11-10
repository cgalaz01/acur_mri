import os
import re

from typing import Any, Dict, Union
from pathlib import Path

import pydicom

import plotly.graph_objects as go


class MetadataSplit():
    
    __dicom_tags = ['MRAcquisitionType', 'SliceThickness', 'RepetitionTime', 'EchoTime',
                    'NumberOfAverages', 'SpacingBetweenSlices', 'EchoTrainLength',
                    'FlipAngle', 'PixelSpacing', 'AcquisitionMatrix', 'Rows', 'Columns',
                    'MagneticFieldStrength', 'CardiacNumberOfImages']
    
    
    def __init__(self):
        self.entries = {}
    
    
    @staticmethod
    def get_tag_info(dicom_directory: Union[str, Path]) -> Dict[str, Any]:
        filename = os.listdir(dicom_directory)[0]
        dataset = pydicom.dcmread(os.path.join(dicom_directory, filename))
        
        tags = {}
        for tag_key in MetadataSplit.__dicom_tags:
            try:
                tags[tag_key] = dataset.data_element(tag_key).value
            except:
                tags[tag_key] = None
            
        #if tags['SpacingBetweenSlices'] is None:
        #    tags['SpacingBetweenSlices'] = tags['SliceThickness']
        
        return tags
    
    
    @staticmethod
    def decouple_tags(entry_values: Dict) -> Dict:
        expanded_values = {}
    
        for tag_key in MetadataSplit.__dicom_tags:
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
    
    
    @staticmethod
    def is_similar(entry_a: Dict[str, Any], entry_b: Dict[str, Any]) -> bool:
        def is_any_null(value_a: Any, value_b: Any) -> bool:
            if value_a is None or value_b is None:
                return True
    
        def is_both_null(value_a: Any, value_b: Any) -> bool:
            if value_a is None and value_b is None:
                return True
    
        if entry_a['MRAcquisitionType'] != entry_b['MRAcquisitionType']:
            return False
        
        if not is_both_null(entry_a['SliceThickness'], entry_b['SliceThickness']):
            if (is_any_null(entry_a['SliceThickness'], entry_b['SliceThickness']) or
                abs(entry_a['SliceThickness'] - entry_b['SliceThickness']) > 0.5):
                return False
        
        if not is_both_null(entry_a['RepetitionTime'], entry_b['RepetitionTime']):
            if (is_any_null(entry_a['RepetitionTime'], entry_b['RepetitionTime']) or
                abs(entry_a['RepetitionTime'] - entry_b['RepetitionTime']) > 0.2):
                return False
        
        if not is_both_null(entry_a['EchoTime'], entry_b['EchoTime']):
            if (is_any_null(entry_a['EchoTime'], entry_b['EchoTime']) or
                abs(entry_a['EchoTime'] - entry_b['EchoTime']) > 0.1):
                return False
        
        if entry_a['NumberOfAverages'] != entry_b['NumberOfAverages']:
            return False
        
        if not is_both_null(entry_a['SpacingBetweenSlices'], entry_b['SpacingBetweenSlices']):
            if (is_any_null(entry_a['SpacingBetweenSlices'], entry_b['SpacingBetweenSlices']) or
                abs(entry_a['SpacingBetweenSlices'] - entry_b['SpacingBetweenSlices']) > 0.5):
                return False
        
        if not is_both_null(entry_a['EchoTrainLength'], entry_b['EchoTrainLength']):
            if (is_any_null(entry_a['EchoTrainLength'], entry_b['EchoTrainLength']) or
                abs(entry_a['EchoTrainLength'] - entry_b['EchoTrainLength']) > 5):
                return False
        
        if not is_both_null(entry_a['FlipAngle'], entry_b['FlipAngle']):
            if (is_any_null(entry_a['FlipAngle'], entry_b['FlipAngle']) or
                abs(entry_a['FlipAngle'] - entry_b['FlipAngle']) > 10):
                return False
        
        if not is_both_null(entry_a['PixelSpacing'], entry_b['PixelSpacing']):
            if is_any_null(entry_a['PixelSpacing'], entry_b['PixelSpacing']):
                return False
            
            if abs(entry_a['PixelSpacing'][0] - entry_b['PixelSpacing'][0]) > 0.1:
                return False
            
            if abs(entry_a['PixelSpacing'][1] - entry_b['PixelSpacing'][1]) > 0.1:
                return False
        
            if not is_both_null(entry_a['AcquisitionMatrix'], entry_b['AcquisitionMatrix']):
                if is_any_null(entry_a['AcquisitionMatrix'], entry_b['AcquisitionMatrix']):
                    return False
                
                row_a = entry_a['AcquisitionMatrix'][0] if entry_a['AcquisitionMatrix'][0] != 0 else entry_a['AcquisitionMatrix'][2]
                row_b = entry_b['AcquisitionMatrix'][0] if entry_b['AcquisitionMatrix'][0] != 0 else entry_b['AcquisitionMatrix'][2]
                
                pixel_size_row_a = entry_a['Rows'] * entry_a['PixelSpacing'][0] / row_a
                pixel_size_row_b = entry_b['Rows'] * entry_b['PixelSpacing'][0] / row_b
                
                if abs(pixel_size_row_a - pixel_size_row_b) > 0.5:
                    return False
            
                column_a = entry_a['AcquisitionMatrix'][1] if entry_a['AcquisitionMatrix'][1] != 0 else entry_a['AcquisitionMatrix'][3]
                column_b = entry_b['AcquisitionMatrix'][1] if entry_b['AcquisitionMatrix'][1] != 0 else entry_b['AcquisitionMatrix'][3]
                
                pixel_size_column_a = entry_a['Columns'] * entry_a['PixelSpacing'][1] / column_a
                pixel_size_column_b = entry_b['Columns'] * entry_b['PixelSpacing'][1] / column_b
                
                if abs(pixel_size_column_a - pixel_size_column_b) > 0.5:
                    return False
        
        if entry_a['MagneticFieldStrength'] != entry_b['MagneticFieldStrength']:
            return False
        
        if entry_a['CardiacNumberOfImages'] != entry_b['CardiacNumberOfImages']:
            return False
        
        return True
    
    
    def get_split_id(self, type_label: str, anatomy_label: Union[str, None],
                     metadata: Dict[str, Any]) -> int:
        
        #key = type_label + '+' + ('' if anatomy_label is None else anatomy_label)
        key = type_label + ('' if anatomy_label is None else '_' + anatomy_label)
        
        split_id = -1
        
        if key in self.entries:
            entry_list = self.entries[key]
            for i in range(len(entry_list)):
                if self.is_similar(metadata, entry_list[i]['values']):
                    entry_list[i]['count'] += 1
                    split_id = i + 1
                    return split_id
            
            new_entry = {'values': metadata, 'count': 1}
            entry_list.append(new_entry)
            split_id = len(entry_list)
        else:
            entry = [{'values': metadata, 'count': 1}]
            self.entries[key] = entry
            split_id = 1    
            
        return split_id
    
    
    def visualise_split(self, output_path: Union[str, Path]) -> None:
        
        if output_path is None:
            output_path = Path('.')
        new_output_path = os.path.join(output_path, 'splits')
        os.makedirs(new_output_path, exist_ok=True)
        
        for key, values in self.entries.items():
            label = [key]
            color = ['blue']
            source = []
            target = []
            value = []
            for i in range(len(values)):
                label.append(str(i + 1))
                color.append('red')
                source.append(0)
                target.append(i + 1)
                value.append(values[i]['count'])
                
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                  pad = 15,
                  thickness = 10,
                  line = dict(color = "black", width = 0.25),
                  label = label,
                  color = color
                ),
                link = dict(
                  source = source, # indices correspond to labels, eg A1, A2, A1, B1, ...
                  target = target,
                  value = value
              ))])
            
            fig.update_layout(title_text=key + ' Breakdown', font_size=14)
                
            fig.write_html(os.path.join(new_output_path, key + '.html'))
            
        import matplotlib.pyplot as plt
        import numpy as np
        
        key = 'CINE_LVSA'
        values = self.entries[key]
        data = []
        for i in values:
            data.append(i['count'])
        
        print(data)
        fig = plt.figure()
        plt.title('CINE LVSA Groups Split')
        plt.xlabel('Group Index')
        plt.ylabel('Total Datasets')
        #plt.hist(data, bins=range(len(data), len(data) + 1, 1))
        
        plt.bar(np.arange(len(data)), data)
        fig.savefig('catalogue_output\\cine_lvsa_groups.png', bbox_inches='tight')
        
