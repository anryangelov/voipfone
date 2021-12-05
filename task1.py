import string
import itertools
import pathlib


def iter_suffixes():
    for number in itertools.count(start=1):
        for result in itertools.product(string.ascii_uppercase, repeat=number):
            yield ''.join(result)


def get_existing_filenames():
    return {p.name for p in pathlib.Path('.').iterdir()}


def get_file_object(prefix):
    existing_filenames_set = get_existing_filenames()
    for suffix in iter_suffixes():
        candidate_filename = prefix + suffix
        if candidate_filename not in existing_filenames_set:  # could be worked without this
            try:
                return open(candidate_filename, 'x')  # open for exclusive creation
            except FileExistsError:
                continue
