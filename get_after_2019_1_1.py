import os
import shutil
import csv
from tqdm import tqdm
import random
from datetime import datetime


data_dir_path = '/shared/vida/processed'
# dataset_dir = 'EdNet-KT1'
dataset_dir = 'payment'

if dataset_dir == 'EdNet-KT1':
    time_shift = 213563
elif dataset_dir == 'payment':
    time_shift = 0

timestamp_2019_1_1 = int(datetime.strptime('2019-01-01 00:00:00.0', '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)

after_2019_file_list = []
user_files = os.listdir(f'{data_dir_path}/{dataset_dir}')
for file in tqdm(user_files):
    with open(f'{data_dir_path}/{dataset_dir}/{file}', 'r') as f_r:
        reader = csv.reader(f_r)
        next(reader)
        timestamp = next(reader)[0]
        timestamp = int(timestamp) + time_shift
        if timestamp > timestamp_2019_1_1:
            after_2019_file_list.append(file)

after_2019_dir = f'{dataset_dir}_after_2019'
os.makedirs(f'{data_dir_path}/{after_2019_dir}', exist_ok=True)

for file in tqdm(after_2019_file_list):
    shutil.copy(f'{data_dir_path}/{dataset_dir}/{file}', f'{data_dir_path}/{after_2019_dir}/{file}')
