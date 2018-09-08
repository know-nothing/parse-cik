from raw_parsers.candidates_list import RawParserCandidatesList
from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv, normalize_string
import os

from raw_parsers.results_summary import RawParserResultsSummary
from raw_parsers.simple import RawParserSimple
import re
import logging


class RawParserSubjPage(RawParserSimple):



class RawParserProportionalSubjectPage(RawParserSimple):
    def __init__(self, root_path):
        super(RawParserProportionalSubjectPage, self).__init__(root_path=root_path)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        hrefs = bs_in.find_all('a')
        cands_re = re.compile('сведения о .*кандидатах.*', re.IGNORECASE)
        res_re = re.compile('сводная таблица', re.IGNORECASE)
        out_return = []
        out_2_file = []
        version = self.detect_version(bs_in)

        for elem in hrefs:
            if cands_re.match(elem.text):
                out_return.append([elem.get('href'),
                                   self.make_filename_out('candidates' if version == 1 else 'candidates1'),
                                   RawParserCandidatesList(root_path=self.root_path, version=version)])
                out_2_file.append([elem.text, elem.get('href')])
            if res_re.match(elem.text):
                out_return.append([elem.get('href'),
                                   self.make_filename_out('results'),
                                   RawParserResultsSummary(root_path=self.root_path, version=version)])
                out_2_file.append([elem.text, elem.get('href')])

        array2d_2tsv(out_2_file, fp_out)
        if len(out_2_file) != 2:
            self.logger.error('parsing %s for hrefs to cands and res found %s hrefs, not two' % (self.filename_in, str(len(out_2_file))))
            return []
        # assert len(out_2_file) == 2
        return out_return
        # return []

    """
    определяет вид страницы (замечено 2 вида), в зависимости от которого идёт дальнейший парсинг
    v1 - более разухабистая на вид, с большим числом элементов-таблиц
    v2 - более минималистичная
    """
    def detect_version(self, bs_in):
        trs = bs_in.find_all('td')
        for tr in trs:
            if normalize_string(tr.text) == 'стандартныеотчеты':
                if tr.get('bgcolor') is not None:
                    return 1
                if tr.get('class') is not None:
                    return 2
                self.logger.error("Version pointer found but cannot recognize in " + self.filename_in_full)
                return 1
        self.logger.error("Version pointer was not found in " + self.filename_in_full)
        return 1


class RawParserMajorSubjPage


class RawParserMajorSubjPageWithSubregs(RawParserSimple):
    def __init__(self, root_path=None, version=None):
        super().__init__(root_path, version)

    def parse(self, bs_in, fp_out):
        pass

    """ subregs [[name, link], ...]"""
    def find_subregions(self, bs_in):
        out = []
        forms = bs_in.find_all('form')
        if (forms is None) | (len(forms) == 0):
            return None
        for form in forms:
            go_reg = form.get('name')
            if (go_reg) & (go_reg == 'go_reg'):
                opts = form.find_all('option')
                for opt in opts:
                    out.append([opt.text.strip(), opt.get('value')])
        return out