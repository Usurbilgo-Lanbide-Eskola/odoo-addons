# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Link instance to survey",
    "version": "14.0.1.0.2",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "survey",
    ],
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "views/survey_view.xml",
        "wizard/create_surveys_from_template_view.xml",
    ],
    "installable": True,
}
