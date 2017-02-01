# -*- encoding: utf-8 -*-
import os
import six
import json
import functools

from odoo_rpc_client.utils import (normalizeSField,
                                   wpartial,
                                   preprocess_args,
                                   stdcall,
                                   UConverter,
                                   ustr,
                                   DirMixIn,
                                   AttrDict)

__all__ = ('ustr',
           'AttrDict',
           'DirMixIn',
           'UConverter',
           'wpartial',
           'makedirs',
           'json_read',
           'json_write',
           'xinput',
           )


# Python 2/3 workaround in raw_input
try:
    xinput = raw_input
except NameError:
    xinput = input


def makedirs(path):
    """ os.makedirs wrapper. No errors raised if directory already exists

        :param str path: directory path to create
    """
    try:
        os.makedirs(path)
    except os.error:
        pass


def json_read(file_path):
    """ Read specified json file
    """
    with open(file_path, 'rt') as json_data:
        data = json.load(json_data)
    return data


def json_write(file_path, *args, **kwargs):
    """ Write data to specified json file

        Note, this function uses dumps function to convert data to json first,
        and write only if conversion is successfule. This allows to avoid
        loss of data when rewriting file.
    """
    # note, using dumps instead of dump, because we need to check if data will
    # be dumped correctly. using dump on incorect data, causes file to be half
    # written, and thus broken
    json_data = json.dumps(*args, **kwargs)

    with open(file_path, 'wt') as json_file:
        json_file.write(json_data)
