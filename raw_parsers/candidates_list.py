from raw_parsers.candidate_card import RawParserCandidateCard
from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv, normalize_string
import os
from raw_parsers.simple import RawParserSimple
import re


class RawParserCandidatesList(RawParserSimple):
    def __init__(self, root_path, version):
        super(RawParserCandidatesList, self).__init__(root_path=root_path, version=version)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        if self.version == 1:
            p = RawParserCandidatesListV1(self.root_path)
            p.filename_in_full = self.filename_in_full
            return p.parse(bs_in, fp_out)
        if self.version == 2:
            p = RawParserCandidatesListV2(self.root_path)
            p.filename_in_full = self.filename_in_full
            arr_out = p.parse(bs_in, fp_out)
            # get all other pages
            hrefs = bs_in.find_all('a')
            for el in hrefs:
                href = el.get('href')
                if (href is not None) & (href.find('number=') > 1):
                    num = normalize_string(el.text)
                    if (href.find('number=' + num) > 0) & (num != '1'):
                        # href found
                        arr_out.append([href,
                                        os.path.join(os.path.dirname(self.filename_in_full), 'candidates' + num + '.html'),
                                        RawParserCandidatesListV2(self.root_path)])
            return arr_out
        self.logger.error("Unrecognized version in " + self.filename_in_full)
        return []

    def parse_candlist(self, bs_in, header_elem_name):
        tables = bs_in.find_all('table')

        tparser = HtmlTableParser(CombinedRowExtractor(row_extractor_simple, row_extractor_href))
        arr = None

        for table in tables:
            # big candidates table
            if (not tparser.has_child_tables(table)) and (table.find(header_elem_name) is not None):
                arr = tparser(table)

        return arr


class RawParserCandidatesListV1(RawParserCandidatesList):
    def __init__(self, root_path):
        super(RawParserCandidatesListV1, self).__init__(root_path=root_path, version=1)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        arr = self.parse_candlist(bs_in, 'tr')
        if arr is None:
            self.logger.error("Candidates not found in " + self.filename_in_full)
            return []
        # ФИО в первом столбце, ссыль - в последнем
        basename = os.path.dirname(self.filename_in_full)
        array2d_2tsv(arr, fp_out)
        return [[row[len(row) - 1],
                 os.path.join(basename, row[0] + '.html'),
                 RawParserCandidateCard(self.root_path, version=1)] for row in arr]


class RawParserCandidatesListV2(RawParserCandidatesList):
    def __init__(self, root_path):
        super(RawParserCandidatesListV2, self).__init__(root_path=root_path, version=2)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        arr = self.parse_candlist(bs_in, 'thead')
        if arr is None:
            self.logger.error("Candidates not found in " + self.filename_in_full)
            return []
        basename = os.path.dirname(self.filename_in_full)
        # ФИО во втором столбцеб ссыль - в последнем
        array2d_2tsv(arr, fp_out)
        return [[row[len(row) - 1],
                os.path.join(basename, row[1] + '.html'),
                RawParserCandidateCard(self.root_path, version=2)] for row in arr]
