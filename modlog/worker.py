import threading
import time
from datetime import datetime

from modlog import api, data
from modlog.common import get_logger
from modlog.data import db

log = get_logger('worker')
update_limit = 100
upper_limit = 500
historical_ok = False


def format_date(t):
    return datetime.utcfromtimestamp(t).isoformat()


def worker():
    if not db.ready:
        log.warning('Database is disabled. Worker has finished.')
        return

    log.debug('Fetching the first entry...')
    entries = api.get_entries(limit=1)
    if not len(entries):
        log.info('No entries were found on remote modlog. Worker has finished.')
        return

    log.debug('Fetching the oldest entry...')
    oldest = next(db.get_entries(limit=1, descending=False), None)
    oldest_id = oldest.get('id') if oldest else None
    log.debug('The query returned %s', oldest_id)

    if oldest:
        log.info('Starting entries update...')
        newest = next(db.get_entries(limit=1), None)
        log.info('Newest entry is %s from %s', newest.get('id'), format_date(newest.get('created_utc')))

        total_updated = 0
        while True:
            global update_limit
            results = list(data.get_entries(limit=update_limit))
            total_updated += len(results)

            newest_found = next(x for x in results if x.get('id') == newest.get('id'))
            if newest_found:
                found_idx = results.index(newest_found)
                total_updated -= (len(results) - found_idx)
                break
            else:
                update_limit = upper_limit

        log.info('Update finished, %d entries loaded.', total_updated)

    global historical_ok
    if not historical_ok:
        total_loaded = 0
        log.info('Starting historical entries fetch...')

        while True:
            result = data.get_entries(after=oldest_id, limit=upper_limit)
            log.info('%d entries loaded, after=%s', len(result), oldest_id)
            total_loaded += len(result)

            if len(result) < upper_limit:
                log.info('Historical load finished, %d entries loaded.', total_loaded)
                break
            else:
                oldest_id = result[-1]['id']

        historical_ok = True

    log.info('Worker has finished working.')


class WorkerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop = threading.Event()

    def stop(self):
        log.info('Stop called')
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        try:
            log.info('Worker thread started')
            while True:
                log.info('Worker is now starting')
                worker()
                log.info('sleeping 10 seconds')
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()


if __name__ == '__main__':
    worker()
