import csv
from tqdm import tqdm
import os
from datetime import datetime
import math


data_dir_path = '/shared/vida/2020.6.1/'
questions_file = 'SELECT_t___FROM_public_questions_t_ORDER.csv'
explanations_file = 'SELECT_t___FROM_public_explanations_t_OR.csv'
lectures_file = 'SELECT_t___FROM_public_lectures_t_ORDER_.csv'
question_labels_file = 'SELECT_t___FROM_public_question_labels_t.csv'
EdNet_dir_path = '/shared/vida/processed/EdNet-KT1_public'


# explanations file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
question_id_answer_dic = {}
question_id_explanation_id_dic = {}
with open(data_dir_path + explanations_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, view_tree, question_id, created_at, updated_at, correct_answer, order = lines[i]
        question_id = int(question_id)

        if question_id in question_id_answer_dic:
            if question_id_answer_dic[question_id] != correct_answer:
                question_id_answer_dic[question_id] = None
        else:
            question_id_answer_dic[question_id] = correct_answer
        question_id_explanation_id_dic[question_id] = id
print(f'Done {explanations_file}')


# print question_id that correct_answer is changed
for question_id, correct_answer in question_id_answer_dic.items():
    if correct_answer is None:
        print(question_id)


# question labels file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
question_id_tags_dic = {}
with open(data_dir_path + question_labels_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, question_id, label_id, created_at, updated_at = lines[i]
        question_id = int(question_id)
        label_id = int(label_id)
        if question_id not in question_id_tags_dic:
            question_id_tags_dic[question_id] = []
        question_id_tags_dic[question_id].append(label_id)
print(f'Done {question_labels_file}')


# questions file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
question_id_info_dic = {}
with open(data_dir_path + questions_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, raw_fbid, view_tree, passage_box_id, created_at, updated_at, pack_type, pack_id, order, status, locale = lines[i]
        if locale == 'ja':
            continue

        question_id = int(id)
        bundle_id = pack_id
        explanation_id = question_id_explanation_id_dic[question_id]
        correct_answer = question_id_answer_dic[question_id]
        part = pack_type[-1]

        tags_str = ''
        if question_id in question_id_tags_dic:
            tags = list(set(question_id_tags_dic[question_id]))
            tags.sort()
            for tag in tags:
                tags_str += str(tag) + ';'
            tags_str = tags_str.strip(';')

        is_deployed = False

        question_id_info_dic[question_id] = [question_id, bundle_id, explanation_id, correct_answer, part, tags_str, is_deployed]
print(f'Done {questions_file}')


# lectures file은 updated at 기준으로 정렬되어 있어야 함 (old to new)
lecture_id_info_dic = {}
with open(data_dir_path + lectures_file, 'r') as f_r:
    lines = [line for line in csv.reader(f_r)]
    for i in tqdm(range(1, len(lines))):
        id, video_id, note_id, created_at, updated_at, label_id, priority, type_of, part, status, locale = lines[i]
        if locale == 'ja':
            continue

        lecture_id = int(id)
        is_deployed = False
        if lecture_id in lecture_id_info_dic:
            print('duplicate')

        lecture_id_info_dic[lecture_id] = [lecture_id, label_id, part, type_of, is_deployed]
print(f'Done {lectures_file}')


user_files = os.listdir(f'{EdNet_dir_path}')
for file in tqdm(user_files):
    with open(f'{EdNet_dir_path}/{file}', 'r') as f_r:
        lines = [line for line in csv.reader(f_r)]
        for i in range(1, len(lines)):
            timestamp, content_id, user_answer, elapsed_time, task_container_id = lines[i]
            if content_id[0] == 'q':
                question_id = int(content_id[1:])
                question_id_info_dic[question_id][-1] = True
            if content_id[0] == 'l':
                lecture_id = int(content_id[1:])
                lecture_id_info_dic[lecture_id][-1] = True


# output questions.csv
question_id_info_list = list(question_id_info_dic.values())
question_id_info_list.sort()
with open('/shared/vida/processed/questions_public.csv', 'w') as f_w:
    f_w.write('question_id,bundle_id,correct_answer,part,tags\n')
    for question_id, bundle_id, explanation_id, correct_answer, part, tags, is_deployed in question_id_info_list:
        if correct_answer is None or not is_deployed:
            continue
        f_w.write(f'q{question_id},b{bundle_id},{correct_answer},{part},{tags}\n')


# output lectures.csv
lecture_id_info_list = list(lecture_id_info_dic.values())
lecture_id_info_list.sort()
with open('/shared/vida/processed/lectures_public.csv', 'w') as f_w:
    f_w.write('lecture_id,tag,part,type_of\n')
    for lecture_id, tag, part, type_of, is_deployed in lecture_id_info_list:
        if not is_deployed:
            continue
        f_w.write(f'l{lecture_id},{tag},{part},{type_of}\n')

