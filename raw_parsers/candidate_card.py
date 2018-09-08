from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv, normalize_string
import os
from raw_parsers.simple import RawParserSimple
import re


class RawParserCandidateCard(RawParserSimple):
    def __init__(self, root_path, version):
        super(RawParserCandidateCard, self).__init__(root_path=root_path, version=version)

    """output: [[href, filename, parser],..]"""
    def parse(self, bs_in, fp_out):
        tparcer = HtmlTableParser()
        tables = [tparcer(_) for _ in bs_in.find_all('table')]
        if self.version == 1:
            tables = list(filter(lambda x: len(x) == 11, tables))
            if len(tables) == 1:
                array2d_2tsv(tables[0], fp_out)
                return []
            self.logger.error("Error in parsing. Found several potential tables in " + self.filename_in_full)
            return []
        if self.version == 2:
            tables = list(filter(lambda x: len(x) == 11, tables))
            if len(tables) == 1:
                array2d_2tsv(tables[0][1:], fp_out)
                return []
            self.logger.error("Error in parsing. Found several potential tables in " + self.filename_in_full)
            return []
        return []
