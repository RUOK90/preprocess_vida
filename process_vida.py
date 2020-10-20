from tqdm import tqdm
import pandas as pd
import csv
import time
import sys
from datetime import datetime
import os
import math
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict


data_dir_path = '/shared/vida/2020.6.1/'
questions_file = 'SELECT_t___FROM_public_questions_t_ORDER.csv'
question_labels_file = 'SELECT_t___FROM_public_question_labels_t.csv'
explanations_file = 'SELECT_t___FROM_public_explanations_t_OR.csv'
lectures_file = 'SELECT_t___FROM_public_lectures_t_ORDER_.csv'
user_resource_file = 'user_resource.csv'
students_file = 'students_final_ver2.csv'
tcr_file = 'tcr_final_ver2.csv'
payments_file = 'payments_final_ver2.csv'
offers_file = 'offers_final_ver2.csv'


offers_num_lines = 25791988
tcr_num_lines = 252320252


debug = False
debug_read_limit = 10000
if debug:
    offers_num_lines = debug_read_limit
    tcr_num_lines = debug_read_limit


# questions file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
content_id_locale_dic = {}
content_id_bundle_id_dic = {}
bundle_id_question_cnt_dic = defaultdict(int)
with open(data_dir_path + questions_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, raw_fbid, view_tree, passage_box_id, created_at, updated_at, pack_type, pack_id, order, status, locale = lines[i]
        id = int(id)

        content_id_locale_dic[f'q{id}'] = locale
        content_id_bundle_id_dic[f'q{id}'] = pack_id
        bundle_id_question_cnt_dic[pack_id] += 1
print(f'Done {questions_file}')


# explanations file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
with open(data_dir_path + explanations_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, view_tree, question_id, created_at, updated_at, correct_answer, order = lines[i]

        content_id_bundle_id_dic[f'x{id}'] = content_id_bundle_id_dic[f'q{question_id}']
print(f'Done {explanations_file}')


# lectures file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
lecture_id_tags_dic = {}
with open(data_dir_path + lectures_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, video_id, note_id, created_at, updated_at, label_id, priority, type_of, part, status, locale = lines[i]
        content_id_bundle_id_dic[f'l{id}'] = None
        content_id_locale_dic[f'l{id}'] = locale
print(f'Done {lectures_file}')


offer_id_integration_diagnosis_dic = {}
with open(data_dir_path + offers_file, 'r') as f_r:
    reader = csv.reader(f_r)
    next(reader)
    for i in tqdm(range(1, offers_num_lines)):
        id, student_id, typ = next(reader)
        if typ == 'integration_diagnosis':
            offer_id_integration_diagnosis_dic[id] = True
print(f'Done {offers_file}')


pk_user_id_dic = {}
with open(data_dir_path + user_resource_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        pk = lines[i][0]
        pk_user_id_dic[pk] = i
print(f'Done {user_resource_file}')


student_id_user_id_country_dic = {}
with open(data_dir_path + students_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, pk, email, nickname, latest_score, target_score, examination_date, feature, last_activity_at, created_at, updated_at, provider, sign_up_platform, sign_up_agent, confirmation_email, confirmed_at, sign_up_at, anonymous_platform, first_country, admin = lines[i]
        if admin == 'true':
            continue
        student_id_user_id_country_dic[id] = {'user_id': pk_user_id_dic[pk], 'country': 'KR'}
print(f'Done {students_file}')


student_id_interactions_dic = {}
with open(data_dir_path + payments_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, student_id, payment_item_id, info_type, info_id, pay_method, origin_amount, payed_amount, refunded_amount, discounted_amount, payed_at, refunded_at, status, created_at, updated_at, paid_point, remarks, paid_amount_krw, paid_amount_usd, country = lines[i]

        if student_id not in student_id_user_id_country_dic:
            continue
        elif country == 'JP':
            student_id_user_id_country_dic[student_id]['country'] = 'JP'
            continue

        if student_id not in student_id_interactions_dic:
            student_id_interactions_dic[student_id] = []

        payed_at = int(datetime.strptime(payed_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
        student_id_interactions_dic[student_id].append([payed_at, f'p{payment_item_id}', '', '', '', ''])
        content_id_bundle_id_dic[f'p{payment_item_id}'] = None

        if status == 'cancelled' or status == '	cancelled_partial':
            refunded_at = int(datetime.strptime(refunded_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)
            student_id_interactions_dic[student_id].append([refunded_at, f'r{payment_item_id}', '', '', '', ''])
            content_id_bundle_id_dic[f'r{payment_item_id}'] = None
print(f'Done {payments_file}')


with open(data_dir_path + tcr_file, 'r') as f_r:
    reader = csv.reader(f_r)
    next(reader)
    for i in tqdm(range(1, tcr_num_lines)):
        id, task_id, student_id, is_studied, value_type, user_answer, correct_answer, elapsed_time_in_ms, eliminated_choices, content_id, content_type, offer_id, created_at, updated_at, task_container_id = next(reader)

        if is_studied == 'false':
            continue
        elif content_type == 'watchingLecutre':
            continue
        elif student_id not in student_id_user_id_country_dic:
            continue
        elif student_id_user_id_country_dic[student_id]['country'] == 'JP':
            continue

        updated_at = int(datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)

        if student_id not in student_id_interactions_dic:
            student_id_interactions_dic[student_id] = []

        if content_type == 'solvingQuestion':
            if f'q{content_id}' not in content_id_bundle_id_dic:
                continue
            if content_id_locale_dic[f'q{content_id}'] == 'ja':
                student_id_user_id_country_dic[student_id]['country'] = 'JP'
                continue

            elapsed_time_in_ms = int(elapsed_time_in_ms)
            student_id_interactions_dic[student_id].append([updated_at, f'q{content_id}', elapsed_time_in_ms, user_answer, offer_id, task_container_id])

        elif content_type == 'watchingExplanation':
            if f'x{content_id}' not in content_id_bundle_id_dic:
                continue
            student_id_interactions_dic[student_id].append([updated_at, f'x{content_id}', '', '', offer_id, task_container_id])

        elif content_type == 'watchingLecture':
            if f'l{content_id}' not in content_id_bundle_id_dic:
                continue
            if content_id_locale_dic[f'l{content_id}'] == 'ja':
                student_id_user_id_country_dic[student_id]['country'] = 'JP'
                continue
            student_id_interactions_dic[student_id].append([updated_at, f'l{content_id}', '', '', offer_id, task_container_id])
print(f'Done {tcr_file}')


interaction_len_cnt_dic = defaultdict(int)
interaction_len = []
dummy_elapsed_time_in_ms = 0
bundle_error_user_cnt = 0

##############################################################################
for student_id, interactions in tqdm(student_id_interactions_dic.items()):
    if len(interactions) == 0:
        continue
    elif student_id not in student_id_user_id_country_dic:
        continue
    elif student_id_user_id_country_dic[student_id]['country'] == 'JP':
        continue

    interactions.sort()

    n_questions = 0
    bundle_error = False
    output_EdNet_KT1_interactions = []
    output_payment_interactions = []
    prev_bundle_last_timestamp = None
    bundle = []
    task_container_id_dic = {}
    for i in range(len(interactions)):
        updated_at, content_id, elapsed_time_in_ms, user_answer, offer_id, task_container_id = interactions[i]

        if i == len(interactions) - 1:
            next_updated_at = next_content_id = next_elapsed_time_in_ms = next_user_answer = next_offer_id = next_task_container_id = None
        else:
            next_updated_at, next_content_id, next_elapsed_time_in_ms, next_user_answer, next_offer_id, next_task_container_id = interactions[i+1]

        if content_id[0] == 'q':
            n_questions += 1
            is_diagnosis = 1 if offer_id in offer_id_integration_diagnosis_dic else 0
            interactions[i].extend([is_diagnosis, ''])
            bundle.append(interactions[i])

            bundle_id = content_id_bundle_id_dic[content_id]
            if i == len(interactions) - 1:
                next_bundle_id = None
                next_content_type = None
            else:
                next_bundle_id = content_id_bundle_id_dic[next_content_id]
                next_content_type = next_content_id[0]

            if bundle_id != next_bundle_id or content_id[0] != next_content_type or elapsed_time_in_ms != next_elapsed_time_in_ms or task_container_id != next_task_container_id:
                # # check whether the number of questions in bundle is full
                # if len(bundle) != bundle_id_question_cnt_dic[bundle_id]:
                #     bundle_error = True
                #     break
                # # check whether questions in a bundle share same bundle_id, content_type, elapsed_time and task_container_id
                # elif task_container_id in task_container_id_dic:
                #     bundle_error = True
                #     break

                # output bundle to output_interactions
                if elapsed_time_in_ms == 0:
                    if prev_bundle_last_timestamp is None:
                        estimated_elapsed_time_in_ms = 0
                    else:
                        estimated_elapsed_time_in_ms = int((updated_at - prev_bundle_last_timestamp) / len(bundle))

                    for j in range(len(bundle)):
                        bundle[j][-1] = estimated_elapsed_time_in_ms
                        output_EdNet_KT1_interactions.append(bundle[j])
                        output_payment_interactions.append(bundle[j])
                else:
                    for j in range(len(bundle)):
                        output_EdNet_KT1_interactions.append(bundle[j])
                        output_payment_interactions.append(bundle[j])

                task_container_id_dic[task_container_id] = True
                bundle = []
                prev_bundle_last_timestamp = updated_at

        elif content_id[0] == 'x' or content_id[0] == 'l':
            interactions[i].extend([0, ''])
            output_EdNet_KT1_interactions.append(interactions[i])
            prev_bundle_last_timestamp = updated_at

        elif content_id[0] == 'p' or content_id[0] == 'r':
            interactions[i].extend([0, ''])
            output_payment_interactions.append(interactions[i])
            prev_bundle_last_timestamp = updated_at

        else:
            prev_bundle_last_timestamp = updated_at

    if bundle_error:
        bundle_error_user_cnt += 1
        continue
##############################################################################

    EdNet_KT1_public_write_dir_path = '/shared/vida/processed/EdNet-KT1_public/'
    EdNet_KT1_private_write_dir_path = '/shared/vida/processed/EdNet-KT1_private/'
    payment_write_dir_path = '/shared/vida/processed/payment/'
    os.makedirs(EdNet_KT1_public_write_dir_path, exist_ok=True)
    # os.makedirs(EdNet_KT1_private_write_dir_path, exist_ok=True)
    # os.makedirs(payment_write_dir_path, exist_ok=True)

    if len(output_EdNet_KT1_interactions) != 0 and n_questions != 0:
        # output EdNet-KT1_public
        user_id = student_id_user_id_country_dic[student_id]['user_id']
        EdNet_KT1_header = 'timestamp,content_id,user_answer,elapsed_time,task_container_id\n'
        with open(f'{EdNet_KT1_public_write_dir_path}u{user_id}.csv', 'w') as f_w:
            f_w.write(EdNet_KT1_header)
            first_updated_at = output_EdNet_KT1_interactions[0][0]
            for interaction in output_EdNet_KT1_interactions:
                updated_at, content_id, elapsed_time_in_ms, user_answer, offer_id, task_container_id, is_diagnosis, estimated_elapsed_time_in_ms = interaction

                # questions that correct answer is changed
                if content_id in ['q2201', 'q2905', 'q6963', 'q7255', 'q7256', 'q12515']:
                    continue

                if content_id[0] == 'x':
                    content_id = f'e{content_id[1:]}'

                updated_at = updated_at - first_updated_at
                f_w.write(f'{updated_at},{content_id},{user_answer},{elapsed_time_in_ms},{task_container_id}\n')

        # # output EdNet-KT1_private
        # EdNet_KT1_header = 'timestamp,content_id,user_answer,elapsed_time,estimated_elapsed_time\n'
        # with open(f'{EdNet_KT1_private_write_dir_path}u{user_id}.csv', 'w') as f_w:
        #     f_w.write(EdNet_KT1_header)
        #     for interaction in output_EdNet_KT1_interactions:
        #         updated_at, content_id, elapsed_time_in_ms, user_answer, offer_id, task_container_id, is_diagnosis, estimated_elapsed_time_in_ms = interaction
        #         f_w.write(f'{updated_at},{content_id},{user_answer},{elapsed_time_in_ms},{estimated_elapsed_time_in_ms}\n')

        # for statistics
        interaction_len_cnt_dic[len(output_EdNet_KT1_interactions)] += 1
        interaction_len.append(len(output_EdNet_KT1_interactions))

    # # output payment
    # if len(output_payment_interactions) != 0:
    #     payment_header = 'timestamp,content_id,is_diagnosis,user_answer,elapsed_time,estimated_elapsed_time\n'
    #     with open(f'{payment_write_dir_path}{student_id}.csv', 'w') as f_w:
    #         f_w.write(payment_header)
    #         for interaction in output_payment_interactions:
    #             updated_at, content_id, elapsed_time_in_ms, user_answer, offer_id, task_container_id, is_diagnosis, estimated_elapsed_time_in_ms = interaction
    #             f_w.write(f'{updated_at},{content_id},{is_diagnosis},{user_answer},{elapsed_time_in_ms},{estimated_elapsed_time_in_ms}\n')


# for statistics
interaction_len_cnt_list = list(interaction_len_cnt_dic.items())
interaction_len_cnt_list.sort()
interaction_len.sort()
x, y = zip(*interaction_len_cnt_list)
print('min:', x[0])
print('max:', x[-1])
print('mean:', np.mean(interaction_len))
print('median:', np.median(interaction_len))

plt.plot(x, y)
plt.xlabel('number of questions answered')
plt.ylabel('number of students')
plt.savefig('interaction_len-user_cnt.png')
print('bundle_error_user_cnt:', bundle_error_user_cnt)
print('Done')
