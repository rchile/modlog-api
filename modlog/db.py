import pymongo
from pymongo import MongoClient
from modlog.common import get_config


class DB:
    """
    Manages the entries retrieval and insertion from the database.
    Compatible only with MongoDB.
    """
    def __init__(self):
        self._col = None
        self.ready = False

        # If database URI is not set, then this instance will do nothing
        # and return stub/empty data.
        db_uri = get_config('MONGODB_URI')
        if not db_uri:
            print('Database is disabled')
            return

        # Initialize database connection
        print('Connecting to the database...')
        client = MongoClient(db_uri)
        db = client.get_database()
        self._col = db.get_collection('entries')
        self.ready = True
        col_count = self._col.count()

        print('Connected to the database, name:', db.name)
        print('DB entry count:', col_count)

        # Create indexes for data retrieval and to avoid dupes.
        self._col.create_index('id', unique=True)
        self._col.create_index([('created_utc', pymongo.DESCENDING)])

    def get_entries(self, after=None, limit=100, include=False):
        """
        Retrieves entries from the database
        :param after: Timestamp (created_utc parameter) since when the entries will be retrieved.
        :param limit: The maximum amount of entries to be retrieved.
        :param include: Normally, the matched entry with the `after` parameter would be ignored, but it can be
                        included on the query by setting this to true.
        :return: The result of the operation from the database. If the database is not ready,
                 an empty list will be returned.
        """
        if not self.ready:
            return []

        # The `include` parameter determines if the matched entry will be included
        operator = '$lte' if include else '$lt'
        query_filter = {'created_utc': {operator: after}} if after else None

        # Sort by new->old and remove the mongodb's _id attribute.
        return self._col.find(query_filter, limit=limit, sort=[("created_utc", pymongo.DESCENDING)],
                              projection={'_id': 0})

    def get_entry(self, entry_id):
        """
        Fetch a single entry from the database.
        :param entry_id: The `id` value from the entry.
        :return: The entry if found. `None` if not found or if the database is not ready.
        """
        if not self.ready:
            return None

        # Remove the _id attribute.
        entry = self._col.find_one({'id': entry_id}, projection={'_id': 0})
        return entry

    def set_entry_note(self, entry_id, note):
        if not self.get_entry(entry_id):
            return False

        self._col.update_one({'id': entry_id}, {'$set': {'notes': note}})

    def insert_entry(self, entry):
        """
        Insert a single entry to the database. If the entry already exists, then it's updated.
        Nothing will be done if the database is not ready.
        :param entry: The entry to insert into the database.
        :return: The result of the `update_one` operation.
        """
        if not self.ready:
            return None

        return self._col.update_one({'id': entry['id']}, {'$set': entry}, upsert=True)

    def insert_entries(self, entries):
        """
        Bulk insert of entries to the database. Filters out entries already on the database.
        :param entries: A `list` of entries fetched from the reddit API.
        :return: The result of the `insert_many` operation. If the database is not ready, or if no missing
        entries were found, then nothing is done and an empty `list` is returned.
        """
        if not self.ready:
            return []

        # Fetch a list of IDs of entries that are already in the database.
        id_list = [e['id'] for e in entries]
        already_in = self._col.find({'id': {'$in': id_list}}).distinct('id')

        # Create a list of entries that are not in the database, from the list above.
        missing_entries = [e for e in entries if e['id'] not in already_in]

        if len(missing_entries) > 0:
            # If there are missing entries, insert them to the database.
            return self._col.insert_many(missing_entries, ordered=False)
        else:
            return []
