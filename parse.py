from raw_parsers.main_search_result import RawParserMainSearchResult
from raw_parsers.html_table import array2d_2tsv
from raw_parsers.subj_page import RawParserProportionalSubjectPage, RawParserMajorSubjPageWithSubregs
import web_processing
import logging

from raw_parsers.simple import RawParserSimple

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

root_folder = 'C:\\Users\\Roman\\PycharmProjects\\GBC\\parse-cik\\resources'

# p_prop = RawParserMainSearchResult(root_folder, subj_parser=RawParserProportionalSubjectPage)
# t_prop = p_prop('main.03-19.proportional.htm')
# web_processing.get_raw_data(root_folder, t_prop)
#
# p_mixed = RawParserMainSearchResult(root_folder, subj_parser=RawParserMajorSubjPageWithSubregs)
# t_mixed = p_mixed('main.03-19.mixed.htm')
# web_processing.get_raw_data(root_folder, t_mixed)

p_major = RawParserMainSearchResult(root_folder, subj_parser=RawParserMajorSubjPageWithSubregs)
t_major = p_major('main.03-19.major.htm')
web_processing.get_raw_data(root_folder, t_major)