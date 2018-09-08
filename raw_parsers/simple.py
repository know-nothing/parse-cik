import os
import lxml, bs4
import logging


class RawParserSimple(object):
    def __init__(self, root_path=None, version=None):
        super(RawParserSimple, self).__init__()
        self.root_path = root_path
        self.filename_in = ''
        self.filename_in_full = ''
        self.logger = logging.getLogger(str(self.__class__.__name__))
        self.version = version
        self.baseurl = None

    def set_filename_in(self, filename_in):
        self.filename_in = os.path.splitext(filename_in)[0]
        self.filename_in_full = filename_in

    def make_filename_out(self, *path_elems):
        return os.path.join(*([self.filename_in] + list(path_elems))) + '.html'

    """filename_in - path to html starting from ROOT_PATH/<<layer>>/"""
    def __call__(self, filename_in, baseurl=None):
        self.baseurl = baseurl
        self.logger.info('parsing ' + filename_in)
        self.set_filename_in(filename_in)
        abspath_in = os.path.join(self.root_path, 'raw_html', filename_in)
        abspath_stg = os.path.join(self.root_path, 'stg', self.filename_in) + \
                      ('.out' if (self.version is None) else ('.v' + str(self.version)))
        try:
            os.mkdir(os.path.dirname(abspath_stg))
        except Exception:
            pass
        with open(abspath_in, 'r') as a, open(abspath_stg, 'w') as b:
            bs = bs4.BeautifulSoup(a, 'lxml')
            return self.parse(bs, b)

    def parse(self, bs_in, fp_out):
        return []
