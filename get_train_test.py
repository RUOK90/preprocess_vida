import os
import shutil
import csv
from tqdm import tqdm
import random


random.seed(1234)
data_dir_path = '/shared/vida/processed'
EdNet_KT1_dir = 'EdNet-KT1'

file_timestamp_list = []
user_files = os.listdir(f'{data_dir_path}/{EdNet_KT1_dir}')
for file in tqdm(user_files):
    with open(f'{data_dir_path}/{EdNet_KT1_dir}/{file}', 'r') as f_r:
        reader = csv.reader(f_r)
        next(reader)
        timestamp, solving_id, question_id, user_answer, elapsed_time = next(reader)
        file_timestamp_list.append([timestamp, file])
file_timestamp_list.sort(reverse=True)

test_user_list = file_timestamp_list[:int(len(file_timestamp_list)*0.1)]
train_user_list = file_timestamp_list[int(len(file_timestamp_list)*0.1):]
random.shuffle(test_user_list)
test1_user_list = test_user_list[:int(len(test_user_list)/2)]
test2_user_list = test_user_list[int(len(test_user_list)/2):]

train_user_file = f'{EdNet_KT1_dir}_train_users.csv'
test1_user_file = f'{EdNet_KT1_dir}_test1_users.csv'
test2_user_file = f'{EdNet_KT1_dir}_test2_users.csv'
train_dir = f'{EdNet_KT1_dir}_train'
test1_dir = f'{EdNet_KT1_dir}_test1'
test2_dir = f'{EdNet_KT1_dir}_test2'

os.makedirs(f'{data_dir_path}/{train_dir}', exist_ok=True)
os.makedirs(f'{data_dir_path}/{test1_dir}', exist_ok=True)
os.makedirs(f'{data_dir_path}/{test2_dir}', exist_ok=True)

with open(f'{data_dir_path}/{test1_user_file}', 'w') as f_w:
    f_w.write('user\n')
    for timestamp, file in tqdm(test1_user_list):
        f_w.write(f'{file}\n')
        shutil.copy(f'{data_dir_path}/{EdNet_KT1_dir}/{file}', f'{data_dir_path}/{test1_dir}/{file}')

with open(f'{data_dir_path}/{test2_user_file}', 'w') as f_w:
    f_w.write('user\n')
    for timestamp, file in tqdm(test2_user_list):
        f_w.write(f'{file}\n')
        shutil.copy(f'{data_dir_path}/{EdNet_KT1_dir}/{file}', f'{data_dir_path}/{test2_dir}/{file}')

with open(f'{data_dir_path}/{train_user_file}', 'w') as f_w:
    f_w.write('user\n')
    for timestamp, file in tqdm(train_user_list):
        f_w.write(f'{file}\n')
        shutil.copy(f'{data_dir_path}/{EdNet_KT1_dir}/{file}', f'{data_dir_path}/{train_dir}/{file}')

print()

