from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv
import os
from raw_parsers.simple import RawParserSimple
import re


class RawParserResultsSummary(RawParserSimple):
    def __init__(self, root_path, version):
        super(RawParserResultsSummary, self).__init__(root_path=root_path, version=version)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        tables = bs_in.find_all('table')

        tparser = HtmlTableParser()
        founded_t = None
        founded_t_num = 0

        for table in tables:
            if not tparser.has_child_tables(table):
                arr = tparser(table)
                i = len(arr)
                if i > 5:
                    founded_t = arr
                    founded_t_num += 1

        if (founded_t is not None) & (founded_t_num > 1):
            self.logger.error("Found more than one results table (%s) in %s" % (str(founded_t_num), self.filename_in_full))
            return []
        if founded_t is None:
            self.logger.error("Could not found any result table in " + self.filename_in_full)
            return []

        # table found
        out_2_file = []
        for row in founded_t:
            if (len(row) > 3) | (len(row) < 2):
                continue
            if (row[0].strip() == '') | (len(row) == 2):
                out_2_file.append(['-----'])
                continue
            out_2_file.append([_.strip() for _ in row])

        array2d_2tsv(out_2_file, fp_out)
        return []
