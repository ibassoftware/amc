# -*- coding: utf-8 -*-
{
    'name': "amc_custom",

    'summary': """
        Customizations for AMC/LOCK 'N LOCK""",

    'description': """
        - Sales Flow:
            - Only Sales Managers can Confirm order
        - Reports:
            - Delivery Slip
            - Pick List
    """,

    'author': "IBAS",
    'website': "http://www.ibasuite.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'sale', 'sale_management', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/stock.config.settings.xml',
        'data/report_paperformat_data.xml',
        'data/report_data.xml',
        # 'wizard/project_task_state_view.xml',
        'views/layout_templates.xml',
        'views/sale_order_views.xml',
        'views/account_invoice_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_quant_views.xml',
        'views/product_views.xml',
        'views/customer_group_views.xml',
        'wizard/print_picklist_views.xml',
        'wizard/stock_operation_report_views.xml',
        'report/report_invoice.xml',
        'report/report_deliveryslip.xml',
        'report/report_picklist.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}