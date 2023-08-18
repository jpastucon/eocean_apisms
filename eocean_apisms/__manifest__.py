# -*- coding: utf-8 -*-
{
    "name": "Touch Entel Ocean - SMS",
    "version": "1.1",
    "depends": ["base", "mail", "web"],
    "author": "T5 EOcean",
    "license": "GPL-3",
    "images": [],
    "description": """
        Módulo de envío en campañas de SMS usando la puerta de enlace Entel Touch Ocean.

    """,
    "website": "https://app.touch.entelocean.io/",
    "category": "SMS",
    "demo": [],
    "data": [
        "views/assets.xml",
        "security/ir.model.access.csv",
        "views/eoceansms.xml",
    ],
    "active": False,
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ["static/description/banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
