import os
import re

from typing import Dict, List, Union
from pathlib import Path
from itertools import combinations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class Categories():
    class TypeLabels():
        
        @staticmethod
        def mip(sequence_description: str) -> Union[None, str]:
            regex_string = 'mip|m\.i\.p'
            if re.findall(regex_string, sequence_description.lower()):
                return 'MIP_merged'
            
            return None
        
        
        @staticmethod
        def mpr(sequence_description: str) -> Union[None, str]:
            regex_string = 'mpr'
            if re.findall(regex_string, sequence_description.lower()):
                return 'MPR_merged'
            
            return None
        
        
        @staticmethod
        def perfusion(sequence_description: str) -> Union[None, str]:
            regex_string = 'perf'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Perf_merged'
            
            return None
        
        
        @staticmethod
        def qflow(sequence_description: str) -> Union[None, str]:
            regex_string = 'flow'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Qflow_merged'
            
            return None

        
        @staticmethod
        def angio(sequence_description: str) -> Union[None, str]:
            regex_string = 'angio'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Angio_merged'
            
            return None
            

        @staticmethod
        def scout(sequence_description: str) -> Union[None, str]:
            regex_string = 'scout'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Scout_merged'
            
            return None

    
        @staticmethod
        def bb(sequence_description: str) -> Union[None, str]:
            regex_string = 'bb'
            if re.findall(regex_string, sequence_description.lower()):
                return 'BB_merged'
            
            return None

        
        @staticmethod
        def db(sequence_description: str) -> Union[None, str]:
            regex_string = 'db'
            if re.findall(regex_string, sequence_description.lower()):
                return 'DB_merged'
            
            return None

        
        @staticmethod
        def t1w(sequence_description: str) -> Union[None, str]:
            regex_string = '(?=.*t1)^((?!map).)*$'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T1w_merged'
            
            return None
        
        
        @staticmethod
        def t2w(sequence_description: str) -> Union[None, str]:
            regex_string = '(?=.*t2)^((?!map).)*$'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T2w_merged'
            
            return None


        @staticmethod
        def t1(sequence_description: str) -> Union[None, str]:
            regex_string = 't1.*map'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T1_Map'
            
            return None
        
        
        @staticmethod
        def t2(sequence_description: str) -> Union[None, str]:
            regex_string = 't2.*map'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T2_Map'
            
            return None
        
        
        @staticmethod
        def cine(sequence_description: str) -> Union[None, str]:
            regex_string = 'cine'
            if re.findall(regex_string, sequence_description.lower()):
                return 'CINE'
            
            return None


        @staticmethod
        def late_gad(sequence_description: str) -> Union[None, str]:
            regex_string = 'lg|late.*g[a]?d'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Late_Gad'
            
            return None
        
        
        @staticmethod
        def early_gad(sequence_description: str) -> Union[None, str]:
            regex_string = '^eg|eg_|_eg|early.*g[a]?d'
            if re.findall(regex_string, sequence_description.lower()):
                return 'Early_Gad'
            
            return None


        @staticmethod
        def pre_molli(sequence_description: str) -> Union[None, str]:
            regex_string = 'pre.*molli'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T1_Map' #'Pre_MOLLI'
            
            return None
        
        
        
        @staticmethod
        def post_molli(sequence_description: str) -> Union[None, str]:
            regex_string = 'post.*molli'
            if re.findall(regex_string, sequence_description.lower()):
                return 'T1_Map' #'Post_MOLLI'
            
            return None
        
        
    class AnatomyLabels():
        
        @staticmethod
        def two_chamber(sequence_description: str) -> Union[None, str]:
            regex_string = '2ch'
            if re.findall(regex_string, sequence_description.lower()):
                return '2ch'
            
            return None
    

        @staticmethod
        def three_chamber(sequence_description: str) -> Union[None, str]:
            regex_string = '3ch|lvot'
            if re.findall(regex_string, sequence_description.lower()):
                return 'LVOT'
            
            return None


        @staticmethod
        def four_chamber(sequence_description: str) -> Union[None, str]:
            regex_string = '4ch'
            if re.findall(regex_string, sequence_description.lower()):
                return '4ch'
            
            return None


        @staticmethod
        def lvsa(sequence_description: str) -> Union[None, str]:
            regex_string = 'lvsa|sax'
            if re.findall(regex_string, sequence_description.lower()):
                return 'LVSA'
            
            return None


        @staticmethod
        def rvot(sequence_description: str) -> Union[None, str]:
            regex_string = 'rvot'
            if re.findall(regex_string, sequence_description.lower()):
                return 'RVOT'
            
            return None
        
        
        @staticmethod
        def mv(sequence_description: str) -> Union[None, str]:
            regex_string = 'mv'
            if re.findall(regex_string, sequence_description.lower()):
                return 'MV'
            
            return None
        
        
        @staticmethod
        def rv(sequence_description: str) -> Union[None, str]:
            regex_string = '(?=.*rv)^((?!rvot).)*$'
            if re.findall(regex_string, sequence_description.lower()):
                return 'RV'
            
            return None
        
        
    def __init__(self) -> None:
        self.sequence_mapping = {}
        
        self.anatomy_matches = ['2ch', '4ch', 'LVOT', 'LVSA', 'RVOT', 'RV', 'MV']
        self.anatomy_combinations = []
        for i in range(1, len(self.anatomy_matches) + 1):
            combination_list = list(map(list, combinations(self.anatomy_matches, i)))
            #combination_list.sort()
            self.anatomy_combinations.append(combination_list)
        
        self.cine_grouping = {}
        
    
    @staticmethod
    def is_repeat(sequence_description: str) -> bool:
        """
        Checks whether the based sequence description has an indication of
        possible repeat scan. 

        Parameters
        ----------
        sequence_description : str
            The original sequence description.

        Returns
        -------
        bool
            Returns True if the passed sequence is possibly a repeat scan.

        """
        regex_string = ' 2$|repeat$|repetition'
        if re.findall(regex_string, sequence_description.lower()):
            return True
        
        return False
        
    
    @staticmethod
    def get_label(sequence_description: str) -> Dict[str, Union[None, str]]:        
        def get_anatomy_label(sequence_description: str) -> Union[None, str]:
            a_label = Categories.AnatomyLabels.two_chamber(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.three_chamber(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.four_chamber(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.lvsa(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.rvot(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.mv(sequence_description)
            if a_label is not None:
                return a_label
            
            a_label = Categories.AnatomyLabels.rv(sequence_description)
            if a_label is not None:
                return a_label
            
            return None
            
        label = Categories.TypeLabels.mip(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.mpr(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.perfusion(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.qflow(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.angio(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.scout(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.bb(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.db(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.t1w(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.t2w(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': None}
        
        label = Categories.TypeLabels.t1(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.t2(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.cine(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.late_gad(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.early_gad(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.pre_molli(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        label = Categories.TypeLabels.post_molli(sequence_description)
        if label is not None:
            return {'type': label, 'anatomy': get_anatomy_label(sequence_description)}
        
        return {'type': 'Other', 'anatomy': None}
    
    
    def store_sequence_mapping(self, sequence: str, type_label: str,
                               anatomy_label: Union[None, str]) -> None:
        """
        Stores the passed sequence description with the mapped type and anatomy
        labels. Keeps the count for each sequence.

        Parameters
        ----------
        sequence : str
            Sequence description before being mapped to a category.
        type_label : str
            The type label of the sequence as returned from the function get_label().
        anatomy_label : Union[None, str]
            The anatomy label of the sequence as returned from the function get_label().

        Returns
        -------
        None

        """
        
        if sequence in self.sequence_mapping:
            self.sequence_mapping[sequence][2] += 1
        else:
            self.sequence_mapping[sequence] = [type_label, anatomy_label, 1]
    
    
    def visualise_sequence_mapping(self, output_path: Union[str, Path]) -> None:
        # Build the DataFrame structure to pass to the plotly function
        sequence = []
        image_type = []
        image_anatomy = []
        count = []
        
        for sequence_key, list_label in self.sequence_mapping.items():
            sequence.append(sequence_key)
            image_type.append(list_label[0])
            image_anatomy.append(list_label[1] if list_label[1] else 'N/A')
            count.append(list_label[2])
            
        df = pd.DataFrame(dict(sequence=sequence, image_type=image_type,
                               image_anatomy=image_anatomy, count=count))  
        
        df['all'] = 'All'
        fig = px.treemap(df, path=['all', 'image_type', 'image_anatomy', 'sequence'],
                         values='count', title='Sequence Grouping')
        fig.update_layout(uniformtext=dict(minsize=16, mode='hide'))
        
        if output_path is None:
            output_path = Path('.')
        os.makedirs(output_path, exist_ok=True)
        
        fig.write_html(os.path.join(output_path, 'treemap_sequence_grouping.html'))

    @staticmethod
    def __list_to_string(anatomy_list: List[str]) -> str:
        tmp_list = anatomy_list.copy()
        tmp_list.sort()
        anatomy_string = '+'.join(tmp_list)
        return anatomy_string


    """
    def store_cine_grouping(self, patient_id, patient_cine: List[Dict[str, Union[None, str]]]) -> None:        
        if len(patient_cine) == 0:
            return None
            
        if not self.cine_grouping:
            for combination_index in self.anatomy_combinations:
                for i in combination_index:
                    cine_key = Categories.__list_to_string(i)
                    self.cine_grouping[cine_key] = []
                
        cine_anatomy_list = []
        for cine in patient_cine:
            if cine['type'] == 'CINE':
                cine_anatomy_list.append(cine['anatomy'])
                
        #print(cine_anatomy_list)
        cine_key = Categories.__list_to_string(list(set(cine_anatomy_list)))
        self.cine_grouping[cine_key].append(patient_id)        
            
            
    def visualise_cine_grouping(self, output_path: Union[str, Path]) -> None:
        cine_count = []
        for cine_key, patient_list in self.cine_grouping.items():
            if len(patient_list) != 0:
                cine_count.append([cine_key, len(patient_list)])
            
        df = pd.DataFrame(cine_count, columns = ['CINE Anatomy Combinations (non-zero)', 'Count'])
        
        fig = px.bar(df, y='Count', x='CINE Anatomy Combinations (non-zero)', text='Count')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        
        if output_path is None:
            output_path = Path('.')
        os.makedirs(output_path, exist_ok=True)
        
        fig.write_html(os.path.join(output_path, 'cine_grouping.html'))
            
        
        ## Visualise cumulative count
        cine_count = []
        for cine_key, patient_list in self.cine_grouping.items():
                cine_count.append([cine_key, len(patient_list)])
                
        for cine_key, patient_list in self.cine_grouping.items():
            cine_key_list = cine_key.split('+')
            for i in range(1, len(cine_key_list)):
                combination_list = list(map(list, combinations(cine_key_list, i)))
                for individual_combination in combination_list:
                    new_cine_key = Categories.__list_to_string(individual_combination)
                    for j in cine_count:
                        if j[0] == new_cine_key:
                            j[1] += len(patient_list)
                            break
                
        df = pd.DataFrame(cine_count, columns = ['CINE Anatomy Combinations (subset inclusive)', 'Count'])
        
        fig = px.bar(df, y='Count', x='CINE Anatomy Combinations (subset inclusive)', text='Count')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        
        fig.write_html(os.path.join(output_path, 'cine_grouping_subset.html'))
    """
        
    def store_cine_grouping(self, patient_id, patient_cine: List[Dict[str, Union[None, str]]]) -> None:        
        if len(patient_cine) == 0:
            return None
          
        """
        if not self.cine_grouping:
            for image_type in ['CINE', 'Late_Gad', 'Early_Gad', 'T1_Map', 'T2_map']:
                for combination_index in self.anatomy_combinations:
                    for i in combination_index:
                        cine_key = Categories.__list_to_string(i)
                        self.cine_grouping[image_type + '_' + cine_key] = []
        """
                        
                
        cine_anatomy_list = []
        for cine in patient_cine:
            if cine['anatomy'] is None:
                continue
            
            if cine['type'] == 'CINE':
                cine_anatomy_list.append('CINE_' + cine['anatomy'])
            elif cine['type'] == 'Late_Gad':
                cine_anatomy_list.append('Late_Gad_' + cine['anatomy'])
            elif cine['type'] == 'Early_Gad':
                cine_anatomy_list.append('Early_Gad_' + cine['anatomy'])
            elif cine['type'] == 'T1_Map':
                cine_anatomy_list.append('T1_Map_' + cine['anatomy'])
            elif cine['type'] == 'T2_Map':
                cine_anatomy_list.append('T2_Map_' + cine['anatomy'])
                
        #print(cine_anatomy_list)
        if len(cine_anatomy_list) == 0:
            return
        
        cine_key = Categories.__list_to_string(list(set(cine_anatomy_list)))
        if cine_key in self.cine_grouping:
            self.cine_grouping[cine_key].append(patient_id)
        else:
            self.cine_grouping[cine_key] = [patient_id]
            
            
    def visualise_cine_grouping(self, output_path: Union[str, Path]) -> None:
        cine_count = []
        for cine_key, patient_list in self.cine_grouping.items():
            if len(patient_list) != 0:
                cine_count.append([cine_key, len(patient_list)])
            
        cine_prune = []
        for i in range(len(cine_count)):
            if cine_count[i][1] >= 20:
                cine_prune.append(cine_count[i])
        df = pd.DataFrame(cine_prune, columns = ['Image/Anatomy Combinations', 'Count'])
        
        fig = px.bar(df, y='Count', x='Image/Anatomy Combinations', text='Count')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(xaxis_tickangle=0)
        
        if output_path is None:
            output_path = Path('.')
        os.makedirs(output_path, exist_ok=True)
        
        df.to_csv(os.path.join(output_path, 'grouping.csv'))
        fig.write_html(os.path.join(output_path, 'grouping.html'))
            
        
        ## Visualise cumulative count
        cine_count = []
        for cine_key, patient_list in self.cine_grouping.items():
                cine_count.append([cine_key, len(patient_list)])
                
        for cine_key, patient_list in self.cine_grouping.items():
            cine_key_list = cine_key.split('+')
            for i in range(1, len(cine_key_list)):
                combination_list = list(map(list, combinations(cine_key_list, i)))
                for individual_combination in combination_list:
                    new_cine_key = Categories.__list_to_string(individual_combination)
                    for j in cine_count:
                        if j[0] == new_cine_key:
                            j[1] += len(patient_list)
                            break
                
        cine_prune = []
        for i in range(len(cine_count)):
            if cine_count[i][1] >= 20:
                cine_prune.append(cine_count[i])
        df = pd.DataFrame(cine_prune, columns = ['Image/Anatomy Combinations (subset inclusive)', 'Count'])
        
        fig = px.bar(df, y='Count', x='Image/Anatomy Combinations (subset inclusive)', text='Count')
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(xaxis_tickangle=0)
        
        df.to_csv(os.path.join(output_path, 'grouping_subset.csv'))
        fig.write_html(os.path.join(output_path, 'grouping_subset.html'))
