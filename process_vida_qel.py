from tqdm import tqdm
import pandas as pd
import csv
import time
import sys
from datetime import datetime


data_dir_path = '/shared/vida/2020.4.27/'
questions_file = 'content_repo_prd_public_questions.csv'
explanations_file = 'content_repo_prd_public_explanations.csv'
lectures_file = 'content_repo_prd_public_lectures.csv'
tcr_file = 'tcr_final_ver2.csv'


max_elapsed_time_in_ms = 999999999
header = 'timestamp,content_id,elapsed_time,user_answer,correct_answer,eliminated_choices\n'


content_id_bundle_id_dic = {}
with open(data_dir_path + questions_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in range(1, len(lines)):
        id, raw_fbid, view_tree, passage_box_id, created_at, updated_at, pack_type, pack_id, order, status, locale = lines[i]
        content_id_bundle_id_dic[f'q{id}'] = pack_id

question_id_answer_dic = {}
with open(data_dir_path + explanations_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in range(1, len(lines)):
        id, view_tree, question_id, created_at, updated_at, correct_answer, order = lines[i]
        content_id_bundle_id_dic[f'e{id}'] = content_id_bundle_id_dic[f'q{question_id}']
        # if f'q{question_id}' in question_id_answer_dic and question_id_answer_dic[f'q{question_id}'] != correct_answer:
        #     print('Error')
        question_id_answer_dic[f'q{question_id}'] = correct_answer

with open(data_dir_path + lectures_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in range(1, len(lines)):
        id, video_id, note_id, created_at, updated_at, label_id, priority, type_of, part, status, locale = lines[i]
        content_id_bundle_id_dic[f'l{id}'] = None

print('done processing dictionary')

debug = False

if debug:
    write_dir_path_qel = 'qel/'
    write_dir_path_ql = 'ql/'
    write_dir_path_qe = 'qe/'
    write_dir_path_q = 'q/'
else:
    write_dir_path_qel = '/shared/question_explanation_lecture/qel/'
    write_dir_path_ql = '/shared/question_explanation_lecture/ql/'
    write_dir_path_qe = '/shared/question_explanation_lecture/qe/'
    write_dir_path_q = '/shared/question_explanation_lecture/q/'

student_id_interactions_dic = {}
with open(data_dir_path + tcr_file, 'r') as f_r:
    for i, line in tqdm(enumerate(csv.reader(f_r))):
        if i == 0:
            continue
        if debug and i == 100000:
            break

        id, task_id, student_id, is_studied, value_type, user_answer, correct_answer, elapsed_time_in_ms, eliminated_choices, content_id, content_type, offer_id, created_at, updated_at = line

        updated_at = int(datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000)

        if is_studied == 'false' or content_type == 'watchingLecutre':
            print('type 1 err', line)
            continue

        elif content_type == 'solvingQuestion' and (user_answer == ''):
            print('type 2 err', line)
            continue

        # elif content_type == 'solvingQuestion' and (question_id_answer_dic[f'q{content_id}'] != correct_answer):
        #     print('type 3 err', line)
        #     continue

        # if (content_type == 'watchingExplanation' or content_type == 'watchingLecture') and (user_answer != '' or correct_answer != '' or value_type != '' or eliminated_choices != ''):
        #     print('type 3 err', line)
        #     continue

        if student_id not in student_id_interactions_dic:
            student_id_interactions_dic[student_id] = []

        if content_type == 'solvingQuestion':
            if f'q{content_id}' not in content_id_bundle_id_dic:
                # print('type 3 err', line)
                continue
            elapsed_time_in_ms = int(elapsed_time_in_ms)
            correct_answer = question_id_answer_dic[f'q{content_id}']
            student_id_interactions_dic[student_id].append([updated_at, f'q{content_id}', elapsed_time_in_ms, user_answer, correct_answer, eliminated_choices])

        elif content_type == 'watchingExplanation':
            if f'e{content_id}' not in content_id_bundle_id_dic:
                # print('type 3 err', line)
                continue
            student_id_interactions_dic[student_id].append([updated_at, f'e{content_id}', '', '', '', ''])

        elif content_type == 'watchingLecture':
            if f'l{content_id}' not in content_id_bundle_id_dic:
                # print('type 3 err', line)
                continue
            student_id_interactions_dic[student_id].append([updated_at, f'l{content_id}', '', '', '', ''])

for student_id, interactions in tqdm(student_id_interactions_dic.items()):
    if len(interactions) == 0:
        continue

    interactions.sort()

    output_interactions = []
    prev_bundle_last_timestamp = None
    bundle = []
    for i in range(len(interactions)):
        updated_at, content_id, elapsed_time_in_ms, user_answer, correct_answer, eliminated_choices = interactions[i]
        if i == 0:
            prev_updated_at = prev_content_id = prev_elapsed_time_in_ms = prev_user_answer = prev_correct_answer = prev_eliminated_choices = None
        else:
            prev_updated_at, prev_content_id, prev_elapsed_time_in_ms, prev_user_answer, prev_correct_answer, prev_eliminated_choices = interactions[i-1]

        if i == len(interactions) - 1:
            next_updated_at = next_content_id = next_elapsed_time_in_ms = next_user_answer = next_correct_answer = next_eliminated_choices = None
        else:
            next_updated_at, next_content_id, next_elapsed_time_in_ms, next_user_answer, next_correct_answer, next_eliminated_choices = interactions[i+1]

        if content_id[0] == 'q':
            if elapsed_time_in_ms == 0:
                bundle_id = content_id_bundle_id_dic[content_id]
                if i == len(interactions) - 1:
                    next_bundle_id = None
                    next_content_type = None
                else:
                    next_bundle_id = content_id_bundle_id_dic[next_content_id]
                    next_content_type = next_content_id[0]

                bundle.append(interactions[i])
                if bundle_id != next_bundle_id or content_id[0] != next_content_type:
                    # output bundle to output_interactions
                    if prev_bundle_last_timestamp is None:
                        elapsed_time_in_ms = max_elapsed_time_in_ms
                    else:
                        elapsed_time_in_ms = (updated_at - prev_bundle_last_timestamp) / len(bundle)

                    for j in range(len(bundle)):
                        bundle[j][2] = elapsed_time_in_ms
                        output_interactions.append(bundle[j])
                    bundle = []
                    prev_bundle_last_timestamp = updated_at
            else:
                output_interactions.append(interactions[i])
                prev_bundle_last_timestamp = updated_at

        elif content_id[0] == 'e':
            bundle_id = content_id_bundle_id_dic[content_id]
            if i == len(interactions) - 1:
                next_bundle_id = None
                next_content_type = None
            else:
                next_bundle_id = content_id_bundle_id_dic[next_content_id]
                next_content_type = next_content_id[0]

            bundle.append(interactions[i])
            if bundle_id != next_bundle_id or content_id[0] != next_content_type:
                # output bundle to output_interactions
                if prev_bundle_last_timestamp is None:
                    elapsed_time_in_ms = max_elapsed_time_in_ms
                else:
                    elapsed_time_in_ms = (updated_at - prev_bundle_last_timestamp) / len(bundle)

                for j in range(len(bundle)):
                    bundle[j][2] = elapsed_time_in_ms
                    output_interactions.append(bundle[j])
                bundle = []
                prev_bundle_last_timestamp = updated_at

        elif content_id[0] == 'l':
            if i == 0:
                interactions[i][2] = max_elapsed_time_in_ms
            else:
                interactions[i][2] = updated_at - prev_bundle_last_timestamp
            output_interactions.append(interactions[i])
            prev_bundle_last_timestamp = updated_at

    with open(write_dir_path_qel + student_id + '.csv', 'w') as f_w:
        f_w.write(header)
        for interaction in output_interactions:
            timestamp, content_id, elapsed_time, user_answer, correct_answer, eliminated_choices = interaction
            f_w.write(f'{timestamp},{content_id},{elapsed_time},{user_answer},{correct_answer},{eliminated_choices}\n')

    with open(write_dir_path_ql + student_id + '.csv', 'w') as f_w:
        f_w.write(header)
        for interaction in output_interactions:
            timestamp, content_id, elapsed_time, user_answer, correct_answer, eliminated_choices = interaction
            if content_id[0] == 'e':
                continue
            f_w.write(f'{timestamp},{content_id},{elapsed_time},{user_answer},{correct_answer},{eliminated_choices}\n')

    with open(write_dir_path_qe + student_id + '.csv', 'w') as f_w:
        f_w.write(header)
        for interaction in output_interactions:
            timestamp, content_id, elapsed_time, user_answer, correct_answer, eliminated_choices = interaction
            if content_id[0] == 'l':
                continue
            f_w.write(f'{timestamp},{content_id},{elapsed_time},{user_answer},{correct_answer},{eliminated_choices}\n')

    with open(write_dir_path_q + student_id + '.csv', 'w') as f_w:
        f_w.write(header)
        for interaction in output_interactions:
            timestamp, content_id, elapsed_time, user_answer, correct_answer, eliminated_choices = interaction
            if content_id[0] == 'e' or content_id[0] == 'l':
                continue
            f_w.write(f'{timestamp},{content_id},{elapsed_time},{user_answer},{correct_answer},{eliminated_choices}\n')
