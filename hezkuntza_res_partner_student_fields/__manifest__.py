# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza Student Fields",
    "version": "14.0.1.0.3",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "partner_contact_gender", "partner_contact_birthdate",
        "partner_phone_secondary"
    ],
    "excludes": [],
    "data": [
        "views/res_partner_view.xml",
    ],
    "post_init_hook": "activate_hezkuntza_languages",
    "installable": True,
}
