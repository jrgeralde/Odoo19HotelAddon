# -*- coding: utf-8 -*-
{
    'name': "hotel",
    'summary': "Hotel Management System",
    'description': "Hotel Guest Registration and Billing System",
    'author': "ROYTEK",
    'website': "https://johnroygeralde.vercel.app",

    'category': 'Uncategorized',
    'version': '19.0.1.4.0',

    'depends': ['base', 'web'],

    'license': 'LGPL-3',

    'assets': {
        'web.report_assets_common': [
            'hotel/static/src/scss/reportstyles.scss',
        ],
    }, 

    # Always loaded data
    'data': [
        'reports/paperformats.xml',     # LOAD THIS FIRST
        'reports/pageheader.xml',
        'reports/pageheader2.xml',
        'reports/billheader.xml',
        'reports/fromtoheader.xml',
        'reports/guestbill.xml',
        'reports/guestbill2.xml',   
        'reports/hoteltransaction.xml',  # accounting report 
        'reports/hoteltransaction2.xml',  # accounting report 
        'reports/hoteltransaction3.xml',  # accounting report with guest name
        'wizards/roombillrecord_edit.xml',        
        'wizards/roombillrecord_new.xml',
        'wizards/emailguestbill.xml',  # Wizard for emailing guest bill
        'security/ir.model.access.csv',
        'views/mainmenu.xml',
        'views/guestregistration.xml',
        'views/guests.xml',         
        'views/rooms.xml',         
        'views/roomtypes.xml',   
        'views/charges.xml', 
        'views/hoteltransactiondashboard.xml',  # Dashboard report template
    
    ],

    'installable': True,
    'application': True,
}