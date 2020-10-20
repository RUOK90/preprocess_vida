import csv
import os
from tqdm import tqdm
from datetime import datetime


data_dir_path = '/shared/vida/2020.6.1/'
explanations_file = 'SELECT_t___FROM_public_explanations_t_OR.csv'


# explanations file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
question_id_info_dic = {}
with open(data_dir_path + explanations_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, view_tree, question_id, created_at, updated_at, correct_answer, order = lines[i]

        created_at = int(datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
        updated_at = int(datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)

        if created_at != updated_at:
            print('err')

        if question_id not in question_id_info_dic:
            question_id_info_dic[question_id] = correct_answer
        else:
            if question_id_info_dic[question_id] != correct_answer:
                print(question_id)
print(f'Done {explanations_file}')
