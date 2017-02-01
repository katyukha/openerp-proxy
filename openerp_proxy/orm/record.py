""" This module contains classes and logic to handle operations on records
"""
from odoo_rpc_client.orm.record import (Record,
                                        RecordList,
                                        ObjectRecords,
                                        get_record,
                                        get_record_list)


# For backward compatability
RecordRelations = Record
