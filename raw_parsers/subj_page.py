from raw_parsers.candidates_list import RawParserCandidatesList
from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv, normalize_string
import os

from raw_parsers.results_summary import RawParserResultsSummary
from raw_parsers.simple import RawParserSimple
import re
import logging



def get_candlink(bs_in):
    out = []
    hrefs = bs_in.find_all('a')
    cands_re = re.compile('сведения о .*кандидатах.*', re.IGNORECASE)
    for elem in hrefs:
        if cands_re.match(elem.text):
            out.append([elem.text, elem.get('href')])
    return out


def get_reslink(bs_in):
    out = []
    hrefs = bs_in.find_all('a')
    res_re = re.compile('сводная таблица', re.IGNORECASE)
    res_re2 = re.compile('сводный отчет', re.IGNORECASE)
    for elem in hrefs:
        if res_re.match(elem.text):
            out.append([elem.text, elem.get('href')])
    if len(out) == 0:
        for elem in hrefs:
            if res_re2.match(elem.text):
                out.append([elem.text, elem.get('href')])
    return out


class RawParserSubjectPage(RawParserSimple):
    def __init__(self, root_path):
        super(RawParserSubjectPage, self).__init__(root_path=root_path)

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


class RawParserProportionalSubjectPage(RawParserSubjectPage):
    def __init__(self, root_path):
        super(RawParserProportionalSubjectPage, self).__init__(root_path=root_path)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        version = self.detect_version(bs_in)
        out_return = []
        out_2_file = []

        for lnk in get_candlink(bs_in):
            out_return.append([lnk[1],
                               self.make_filename_out('candidates' if version == 1 else 'candidates1'),
                               RawParserCandidatesList(root_path=self.root_path, version=version)])
            out_2_file.append(lnk)

        for lnk in get_reslink(bs_in):
            out_return.append([lnk[1],
                               self.make_filename_out('results'),
                               RawParserResultsSummary(root_path=self.root_path, version=version)])
            out_2_file.append(lnk)

        array2d_2tsv(out_2_file, fp_out)
        if len(out_2_file) != 2:
            self.logger.error('parsing %s for hrefs to cands and res found %s hrefs, not two' % (self.filename_in, str(len(out_2_file))))
            return []
        # assert len(out_2_file) == 2
        return out_return
        # return []


class RawParserMajorSubjPageSubreg(RawParserSubjectPage):
    def __init__(self, root_path=None, version=None):
        super().__init__(root_path)
        self.version = version

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        reslinks = get_reslink(bs_in)
        if len(reslinks) != 1:
            self.logger.error("some troubles with getting results in %s; got reslinks %s" % (self.filename_in_full, str(len(reslinks))))
            return []
        array2d_2tsv([reslinks], fp_out)

        return [[reslinks[0][1],
                 '%s.results%s' % os.path.splitext(self.filename_in_full),
                 RawParserResultsSummary(self.root_path, self.version)]]


class RawParserMajorSubjPageWithSubregs(RawParserSubjectPage):
    def __init__(self, root_path=None):
        super().__init__(root_path)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        cands = get_candlink(bs_in)
        if self.version is None:
            self.version = self.detect_version(bs_in)
        out_return = []
        out_2_file = []

        if cands is None:
            self.logger.error("Cands not found " + self.filename_in_full)
            return []

        for lnk in cands:
            out_return.append([lnk[1],
                               self.make_filename_out('candidates' if self.version == 1 else 'candidates1'),
                               RawParserCandidatesList(root_path=self.root_path, version=self.version)])
            out_2_file.append(lnk)

        subregs = self.find_subregions(bs_in)
        if (subregs is not None) and (len(subregs) > 0):
            self.logger.info("subregs found in " + self.filename_in_full)
            for subreg in subregs:
                out_return.append([subreg[1],
                                   self.make_filename_out(subreg[0].split(' ')[0]),
                                   RawParserMajorSubjPageSubreg(root_path=self.root_path,
                                                                version=self.version)])
                out_2_file.append(subreg)
            array2d_2tsv(out_2_file, fp_out)
            return out_return

        reslinks = get_reslink(bs_in)
        if len(reslinks) != 1:
            self.logger.error("some troubles with getting results in %s; got reslinks %s" % (self.filename_in_full, str(len(reslinks))))
        else:
            out_return.append([reslinks[0][1],
                              self.make_filename_out('results'),
                              RawParserResultsSummary(self.root_path, self.version)])
            out_2_file.append(reslinks[0])

        array2d_2tsv(out_2_file, fp_out)
        return out_return


    """ subregs [[name, link], ...]"""
    def find_subregions(self, bs_in):
        out = []
        forms = bs_in.find_all('form')
        if (forms is None) or (len(forms) == 0):
            return None
        for form in forms:
            go_reg = form.get('name')
            if (go_reg is not None) and (go_reg == 'go_reg'):
                opts = form.find_all('option')
                for opt in opts:
                    if opt.text.strip() != '---':
                        out.append([opt.text.strip(), opt.get('value')])
        return out
