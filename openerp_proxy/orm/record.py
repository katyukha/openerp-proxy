""" This module contains classes and logic to handle operations on records
"""
from odoo_rpc_client.orm.record import (Record,           # noqa
                                        RecordList,       # noqa
                                        ObjectRecords,    # noqa
                                        get_record,       # noqa
                                        get_record_list)  # noqa


# For backward compatability
RecordRelations = Record       # noqa
