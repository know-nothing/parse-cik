import requests
import os
import logging
import time

FORCE = False


def get_data(url, filename_out):
    if (not FORCE) & (os.path.exists(filename_out)):
        logging.info('skipping ' + url)
        return True
    logging.info('getting data from ' + url)
    time.sleep(0.41)
    try:
        resp = requests.get(url)
        os.mkdir(os.path.dirname(filename_out))
    except FileExistsError:
        pass
    except Exception as ex:
        logging.error(str(ex))
        return True

    if resp.status_code == requests.codes.ok:
        with open(filename_out, 'w') as f:
            print(resp.text, file=f)
        return True
    logging.error("res status code " + str(resp.status_code))


def get_raw_data(root_folder, walking_arr):
    i = 0
    for url, filename, parser in walking_arr:
        filename_out = os.path.join(root_folder, 'raw_html', filename)
        if not get_data(url, filename_out):
            break
        i += 1

        get_raw_data(root_folder, parser(filename, url))
