# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza importer photos via smb path",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "hezkuntza_student_importer",
    ],
    "external_dependencies": {"python": ["pysmb"]},
    "excludes": [],
    "data": [
        "views/hezkuntza_student_import_view.xml",
    ],
    "installable": True,
}
