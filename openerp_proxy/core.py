# -*- coding: utf8 -*-
"""
This module provides some classes to simplify access to Odoo server via xmlrpc.

Example ussage of this module

.. code:: python

    >>> cl = Client('server.com', 'dbname', 'some_user', 'mypassword')
    >>> sale_obj = cl['sale_order']
    >>> sale_ids = sale_obj.search([('state','not in',['done','cancel'])])
    >>> sale_data = sale_obj.read(sale_ids, ['name'])
    >>> for order in sale_data:
    ...     print("%5s :    %s" % (order['id'],order['name']))
    >>> product_tmpl_obj = cl['product.template']
    >>> product_obj = cl['product.product']
    >>> tmpl_ids = product_tmpl_obj.search([('name','ilike','template_name')])
    >>> print(product_obj.search([('product_tmpl_id','in',tmpl_ids)]))

    >>> db = Client('erp.host.com', 'dbname='db0', user='your_user')
    >>> so = db['sale.order']
    >>> order_ids = so.search([('state','=','done')])
    >>> order = so.read(order_ids[0])

Also You can call any method (beside private
ones starting with underscore(_)) of any model.
For example following code allows to check
availability of stock moves:

.. code:: python

    >>> db = session.connect()
    >>> move_obj = db['stock.move']
    >>> move_ids = [1234] # IDs of stock moves to be checked
    >>> move_obj.check_assign(move_ids)

Ability to use Record class as analog to browse_record:

.. code:: python

    >>> move_obj = db['stock.move']
    >>> move = move_obj.browse(1234)
    >>> move.state
    ... 'confirmed'
    >>> move.check_assign()
    >>> move.refresh()
    >>> move.state
    ... 'assigned'
    >>> move.picking_id
    ... R('stock.picking', 12)['OUT-12']
    >>> move.picking_id.id
    ... 12
    >>> move.picking_id.name
    ... 'OUT-12'
    >>> move.picking_id_.state
    ... 'assigned'
"""

from odoo_rpc_client.client import Client
