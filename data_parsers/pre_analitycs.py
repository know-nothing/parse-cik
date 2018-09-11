import logging
import re, os
from data_parsers.tsv import array2d_2tsv
from data_parsers.tsv import from_tsv

logger = logging.getLogger(str(__name__))

parties_to_normalize = [['единаяроссия', 'единая россия'],
                        ['кпрф', 'кпрф'],
                        ['коммунистическаяпартияроссийскойфедерации', 'кпрф'],
                        ['коммунистическойпартиироссийскойфедерации', 'кпрф'],
                        ['либерально-демократическаяпартияроссии', 'лдпр'],
                        ['лдпр', 'лдпр'],
                        ['справедливаяроссия', 'справедливая россия']]

parties = ['единая россия', 'кпрф', 'лдпр', 'справедливая россия', 'другие']


def normalize_str(st):
    return re.compile(r'\s').sub('', str(st)).lower()


def get_normalized_party(inp):
    inp_normalized = normalize_str(inp)
    for party in parties_to_normalize:
        if party[0] in inp_normalized:
            return party[1]
    return 'другие'


def get_all_parties_scores(normalized_parties_arr):
    d = dict(normalized_parties_arr)
    return [[p, d.get(p, '0 0%')] for p in parties]


def get_normalized_parties_from_parties_arr(inp_arr):
    out_arr = []
    for row in inp_arr:
        out_arr.append([get_normalized_party(row[len(row) - 2]),
                        row[len(row) - 1]])
    return out_arr


def get_parties_from_res_arr(res_arr):
    parties_stage = False
    arr_out = []
    for i in range(1, len(res_arr)):
        if parties_stage:
            arr_out.append(res_arr[i])
        if res_arr[i][2].strip() == '-----':
            parties_stage = True
    return arr_out


def get_parties(filename_in, filename_out):
    with open(filename_out, 'w') as f_out:
        start_folder = os.path.splitext(filename_in)[0]
        for root, dirs, filenames in os.walk(start_folder, topdown=True):
            if len(dirs) == 0:
                results_found = False
                if 'results.v1' in filenames:
                    res_arr = from_tsv(os.path.join(root, 'results.v1'))
                elif 'results.v2' in filenames:
                    res_arr = from_tsv(os.path.join(root, 'results.v2'))
                else:
                    raise Exception('results not found in ' + root)
                if len(res_arr) > 0:
                    parties = get_parties_from_res_arr(res_arr)
                    array2d_2tsv([_[2:] for _ in parties], f_out)
                else:
                    logger.error("parties not found in " + root)


if __name__ == '__main__':
    get_parties(
        filename_in='C:\\Users\\Roman\\PycharmProjects\\GBC\\parse-cik\\resources\\stg\\main.03-19.proportional.out',
        filename_out='C:\\Users\\Roman\\PycharmProjects\\GBC\\parse-cik\\resources\\raw_data\\analitycs\\proportional_parties.out')

