from collections import defaultdict
from django.db import models
import json
import pickle
import numpy as np
import ast
import urllib.request, urllib.error, urllib.parse
import yaml

class TagField(models.TextField):
    description = "Stores tags in a single database column."

    def __init__(self, delimiter="|", *args, **kwargs):
        self.delimiter = delimiter
        super(TagField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return []
        return value.split(self.delimiter)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if not value:
            return []
        # Otherwise, split by delimiter
        return value.split(self.delimiter)

    def get_prep_value(self, value):
        return self.delimiter.join(value)


class NumpyArrayField(models.TextField):
    description = "Stores a Numpy ndarray."

    def __init__(self, *args, **kwargs):
        super(NumpyArrayField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return np.array([])
        return np.array(pickle.loads(bytes(str(value), "latin-1")))

    def to_python(self, value):
        if isinstance(value, list):
            value = np.array(list)
        if isinstance(value, np.ndarray):
            return value

        if not value:
            return np.array([])
        return np.array(pickle.loads(bytes(str(value), "latin-1")))

    def get_prep_value(self, value):
        if isinstance(value, list):
            return str(pickle.dumps(value, protocol=0), "latin-1")
        elif isinstance(value, np.ndarray):
            return str(pickle.dumps(value.tolist(), protocol=0), "latin-1")
        else:
            raise TypeError("%s is not a list or numpy array" % value)


class DictField(models.TextField):
    description = "Stores a python dictionary"

    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            value = {}
        if isinstance(value, dict):
            return value
        try:
            return ast.literal_eval(value)
        except:
            return(yaml.load(value))

    def to_python(self, value):
        if not value:
            value = {}

        if isinstance(value, dict):
            return value
        try:
            return ast.literal_eval(value)
        except:
            return(yaml.load(value))

    def get_prep_value(self, value):
        if value is None:
            return value

        if isinstance(value, defaultdict):
            value = dict(value)

        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class JSONField(models.TextField):
    description = "Stores a python dictionary"

    def __init__(self, *args, **kwargs):
        super(JSONField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return value
        return json.loads(value)

    def to_python(self, value):
        if not value:
            return value
        if not isinstance(value, str):
            return value
        return json.loads(value)

    def get_prep_value(self, value):
        print("get prep value", value)
        return json.dumps(value)


class DictModel(models.Model):
    data = DictField(max_length=255, primary_key=True)

    class Meta:
        abstract = True

    ## dict methods
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def keys(self):
        return list(self.data.keys())

    def values(self):
        return list(self.data.values())

    def items(self):
        return list(self.data.items())


def sync_database():
    print("This will download a *very* large database.")
    ans = input("  Are you sure you want to proceed? (y/n) [n]: ")
    if ans.lower()[0] != "y":
        return

    loc = input("Where should the database be downloaded to?" + "[/tmp]: ")
    if not loc:
        loc = "/tmp"

    url = "http://oqmd.org/static/downloads/database.tgz"

    file_name = loc + "/" + url.split("/")[-1]
    u = urllib.request.urlopen(url)
    f = open(file_name, "wb")
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes: %s" % (file_name, file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100.0 / file_size)
        status = status + chr(8) * (len(status) + 1)
        print(status, end=" ")
    print()
    f.close()

    msg = "The database has been successfully downloaded."
    msg += "To include in mysql, issue the following commands as root:"
    msg += "mv /tmp/database.tgz /var/lib/mysql"
    msg += "cd /var/lib/mysql && tar -xvf database.tgz"
    msg += "\n"
    msg += 'Note: if you already have a database named "qmdb" this process'
    msg += " will overwrite the existing oqmd database."

    print(msg)
