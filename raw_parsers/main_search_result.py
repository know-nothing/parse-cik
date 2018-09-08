from raw_parsers.html_table import HtmlTableParser, CombinedRowExtractor, row_extractor_href, row_extractor_simple, \
    array2d_2tsv
import os
from raw_parsers.simple import RawParserSimple
from raw_parsers.subj_page import RawParserProportionalSubjectPage


class RawParserMainSearchResult(RawParserSimple):
    def __init__(self, root_path, subj_parser=RawParserSimple):
        super(RawParserMainSearchResult, self).__init__(root_path=root_path)
        self.subj_parser = subj_parser

    def parse(self, bs_in, fp_out):
        tbl = bs_in.find_all('table')[7]
        row_parser = CombinedRowExtractor(row_extractor_simple, row_extractor_href)
        t_parser = HtmlTableParser(row_parser)

        # move dates and fill regions: t -> [[date, region, value, href]]
        currdate = None
        curregion = None
        cursubregion = None
        newt = []
        i = 0
        for row in t_parser(tbl):
            # if date
            if len(row) == 1:
                currdate = row[0]
            else:
                # if row with region
                if len(row) == 3:
                    if row[0].strip() != '':
                        if row[0].startswith('\xa0\xa0'):
                            cursubregion = row[0]
                        else:
                            curregion = row[0]
                            cursubregion = ''

                    newt.append([_.strip() for _ in [str(i), currdate, curregion, cursubregion, row[1], row[2]]])
                else:
                    newt.append([_.strip() for _ in [str(i), currdate, curregion, cursubregion, row[0], row[1]]])
                assert 'http' in newt[i][5]
                i += 1

        array2d_2tsv(newt, fp_out)

        # [[href, filename, parser],..]
        return ([row[5], self.make_filename_out(str(row[0])), self.subj_parser(self.root_path)] for row in newt)
