# -*- coding: utf-8 -*-
{
    'name': 'Material Registration',
    'version': '14.0.1.0.0',
    'summary': 'Material Registration REST API',
    'description': """
        Material Registration module for managing materials,
        material types, buy prices, and related suppliers.
    """,
    'author': 'Fakhrusy Al Asady',
    'category': 'Inventory',
    'depends': [
        'base',
    ],
    'data': [
    'security/ir.model.access.csv',
    'views/material_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}