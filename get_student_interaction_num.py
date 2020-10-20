import csv
import os
from tqdm import tqdm


old_data_dir = '/shared/EdNet/KT1'
new_data_dir = '/shared/vida/processed/EdNet-KT1'
old_student_files = os.listdir(old_data_dir)
new_student_files = os.listdir(new_data_dir)
old_interaction_cnt = 0
new_interaction_cnt = 0


for file in tqdm(old_student_files):
    with open(f'{old_data_dir}/{file}', 'r') as f_r:
        lines = [line for line in csv.reader(f_r)]
        old_interaction_cnt += len(lines) - 1
print(f'Done {old_data_dir}')


for file in tqdm(new_student_files):
    with open(f'{new_data_dir}/{file}', 'r') as f_r:
        lines = [line for line in csv.reader(f_r)]
        new_interaction_cnt += len(lines) - 1
print(f'Done {new_data_dir}')


print('old users: ', len(old_student_files))
print('old interactions: ', old_interaction_cnt)
print('new users: ', len(new_student_files))
print('new interactions: ', new_interaction_cnt)

