from logging import getLogger, Logger
import re


def normalize_string(str_in):
    return re.compile(r'\s').sub('', str(str_in)).lower()


def row_extractor_simple(row):
    return [ele.text.replace('\n', ' ') for ele in row.find_all('td')]


def row_extractor_dummy(row):
    return []


def row_extractor_href(row):
    href = row.find('a')
    if href is not None:
        return [href.get('href')]
    return []


class RowExtractorEnumerate(object):
    """docstring for RowExtractorEnumerate"""

    def __init__(self):
        super(RowExtractorEnumerate, self).__init__()
        self.i = 0

    def __call__(self, row):
        self.i += 1
        return [self.i - 1]


def array2d_2tsv(arr, fout):
    for row in arr:
        print('\t'.join([str(e) for e in row]), file=fout)


class CombinedRowExtractor(object):
    """docstring for CombinedRowExtractor"""

    def __init__(self, *row_extractors):
        super(CombinedRowExtractor, self).__init__()
        self.row_extractors = row_extractors

    def __call__(self, row):
        t = []
        for row_ext in self.row_extractors:
            if row_ext is not None:
                t += row_ext(row)
        return t


class HtmlTableParser(object):
    """docstring for HtmlTableParser"""

    def __init__(self, row_extrator=row_extractor_simple):
        super(HtmlTableParser, self).__init__()
        self.row_extrator = row_extrator
        self.logger = getLogger('HtmlTableParser')

    """returns 2-dim array"""
    def __call__(self, bs_table):
        body = bs_table.find('tbody')
        rows = body.find_all('tr') if body is not None else bs_table.find_all('tr')
        self.logger.debug('tbl height = %s' % (len(rows)))
        return [self.row_extrator(row) for row in rows]

    def has_child_tables(self, bs_table):
        return True if bs_table.find('table') else False