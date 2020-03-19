# -*- coding: utf-8 -*-
{
    'name': "ibas_amc",

    'summary': """
        IBAS Customizations for AMC""",

    'description': """
        Long description of module's purpose
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','sale','account'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
          'security/security_view.xml',
         'views/inventory_view.xml',
         'views/reorder_location_view.xml',
         'views/return_stock_request.xml',
         'views/stock_location.xml',
         'views/account_invoice_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}