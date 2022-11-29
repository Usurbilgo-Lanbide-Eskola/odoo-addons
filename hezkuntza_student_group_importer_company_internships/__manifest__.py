# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza Group Importer and Company Internships Glue Module",
    "version": "14.0.1.0.2",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "hezkuntza_student_group_importer", "company_internships"
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "excludes": [],
    "data": [
        "views/hezkuntza_student_group_view.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
