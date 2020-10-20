import csv
from tqdm import tqdm


data_dir_path = '/shared/vida/2020.6.1/'
old_user_resource_file = 'old_user_resource.csv'
new_user_resource_file = 'new_user_resource.csv'
students_file = 'students_final_ver2.csv'


pk_student_id_dic = {}
with open(data_dir_path + old_user_resource_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        pk = lines[i][0]
        pk_student_id_dic[pk] = i
        student_id = i


student_id += 1
with open(data_dir_path + students_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, pk, email, nickname, latest_score, target_score, examination_date, feature, last_activity_at, created_at, updated_at, provider, sign_up_platform, sign_up_agent, confirmation_email, confirmed_at, sign_up_at, anonymous_platform, first_country, admin = lines[i]

        if admin == 'true':
            continue

        if pk not in pk_student_id_dic:
            pk_student_id_dic[pk] = student_id
            student_id += 1


pk_student_id_list = sorted(list(pk_student_id_dic.items()), key=lambda item: item[1], reverse=False)
with open(data_dir_path + new_user_resource_file, 'w') as f_w:
    f_w.write('pk\n')
    for pk, student_id in pk_student_id_list:
        f_w.write(f'{pk}\n')
