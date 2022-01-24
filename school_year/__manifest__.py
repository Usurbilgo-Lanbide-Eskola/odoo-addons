# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "School Year",
    "version": "14.0.1.0.0",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "contacts",
    ],
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "data/school_year_data.xml",
        "views/school_year_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
}
