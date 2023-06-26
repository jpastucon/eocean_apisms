# -*- coding: utf-8 -*-
{
    "name": "Entel Ocean - Touch",
    "version": "1.0",
    "depends": ["base", "mail", "web"],
    "author": "T5 EOcean",
    "license": "GPL-3",
    "images": [],
    "description": """
        Módulo de envío en campañas de SMS usando la puerta de enlace Entel Touch Ocean.

    """,
    "website": "https://app-qa.touch.entelocean.io/",
    "category": "SMS",
    "demo": [],
    "data": [
        "views/assets.xml",
        #"security/security.xml",
        #"security/ir.model.access.csv",
        "views/eoceansms.xml"
    ],
    "active": False,
    "installable": True,
    "application": True,
    'auto_install': False,
    "images": ["static/description/banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
