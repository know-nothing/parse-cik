import logging
import os

from data_parsers.headers import h_cands_page_v2
from data_parsers.pre_analitycs import get_parties_from_res_arr, get_normalized_parties_from_parties_arr, \
    get_all_parties_scores, get_normalized_party, normalize_str
from data_parsers.tsv import from_tsv, transpose, transpose_with_header, array2d_2tsv


logger = logging.getLogger(str(__name__))
logger.setLevel('INFO')
"""
Нужны элементы 2,10,11 и нормированные партии
"""
def process_res_v2(filename_in):
    raw_table = from_tsv(filename_in)
    if len(raw_table) < 10:
        return [], []
    # getting norm parties
    parts = get_parties_from_res_arr(raw_table)
    parts = get_normalized_parties_from_parties_arr(parts)
    parts = get_all_parties_scores(parts)
    global_num = os.path.basename(raw_table[0][0])
    peop_cnt = raw_table[1][len(raw_table[1]) - 1]
    true_bull = raw_table[10][len(raw_table[1]) - 1]
    false_bull = raw_table[9][len(raw_table[1]) - 1]
    out_arr = [['глобальный номер голосования', global_num],
               ['имя директории', raw_table[1][0]],
               ['число избирателей', peop_cnt],
               ['число недействительных бюллетеней', false_bull],
               ['число действительных бюллетеней', true_bull]]
    out_arr.extend(parts)
    return transpose_with_header(out_arr)[1]


def process_cands_v2(filename_in):
    raw_table = from_tsv(filename_in)
    raw_table2 = []
    for cand in raw_table:
        cand[5] = get_normalized_party(cand[5])
        # cand[1] = os.path.basename()
        raw_table2.append(cand[3:-1])
    return raw_table2


def process_cand_v2(filename_in):
    raw_table = from_tsv(filename_in)
    if len(raw_table) != 10:
        logger.warn("Strange data for candidate in " + filename_in)
        raw_table = raw_table[:10]
    return transpose_with_header(_[-2:] for _ in raw_table)[1]


def join_cands_pers_n_common(pers, common):
    pers_dict = dict((normalize_str(_[0]), _) for _ in common)
    out_arr = []
    for cand in pers:
        out_arr.append(cand + pers_dict[normalize_str(cand[0])][1:])
    return out_arr


def go_proportional(
        filename_in='C:\\Users\\Roman\\PycharmProjects\\GBC\\parse-cik\\resources\\stg\\main.03-19.proportional.out'):
    # harvest dates and regions
    start_folder = os.path.splitext(filename_in)[0]
    out_folder = os.path.splitext(filename_in)[0].replace('stg', 'raw_data')
    arr_results = []
    # arr_cands_common = []
    arr_cands = []
    head_results = ""
    head_cands_common = ""
    head_cand = ""

    for root, dirs, filenames in os.walk(start_folder, topdown=True):
        list_folder = False
        # мы на самой глубине, первого типа результаты нам не нужны
        if 'results.v2' in filenames:
            logger.info(root)
            cands_pers_local = []
            cands_common_local = []
            list_folder = True
            # заберём ID региона из названия папки
            for filename in filenames:
                filename_in = os.path.join(root, filename)
                if filename == 'results.v2':
                    arr_results_tmp = process_res_v2(filename_in)
                    if len(arr_results_tmp) > 0:
                        arr_results.extend(arr_results_tmp)
                    continue
                if 'candidates' in filename:
                    cands_common_local.extend(process_cands_v2(filename_in))
                    continue
                cands_pers_local.extend(process_cand_v2(filename_in))

            arr_cands.extend(join_cands_pers_n_common(cands_pers_local, cands_common_local))
            # harvest results
            # res_arr = from_tsv(os.path.join(root, 'results.v2'))
            # общая часть
            # res_arr_common = res_arr[1:13]

    with open(os.path.join(out_folder, 'results.out'), 'w') as fres:
        array2d_2tsv(fres, head_results, *arr_results)
    with open(os.path.join(out_folder, 'candidates.out'), 'w') as fcands:
        array2d_2tsv(fcands, h_cands_page_v2[1:-1], *arr_cands)


go_proportional()
