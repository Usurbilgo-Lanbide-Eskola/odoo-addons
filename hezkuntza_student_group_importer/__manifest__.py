# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza Student Group Importer",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "hezkuntza_student_importer",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "excludes": [],
    "data": [
        "data/student_group_sequence.xml",
        "security/ir.model.access.csv",
        "views/hezkuntza_group_data_maps_view.xml",
        "views/hezkuntza_student_group_view.xml",
        "views/hezkuntza_student_import_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
