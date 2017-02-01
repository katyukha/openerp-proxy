""" Report printing logic

Best way to generate report is::

    data_records = client['res.partner'].search_records([], limit=10)
    report = client.services.report['res.partner'].generate(data_records)
    report.content

Or if it is desired to save it on disk::

    data_records = client['res.partner'].search_records([], limit=10)
    report = client.services.report['res.partner'].generate(data_records)
    report.save('filename to save report with')


where *report* is instance of *ReportResult* and *report.content*
returns already *base64* decoded content of report,
which could be directly written to file (or
just use *report.save(path)* method)
"""

from odoo_rpc_client.service.report import (ReportError,
                                            ReportResult,
                                            Report,
                                            ReportService)
