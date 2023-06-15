# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza student importer",
    "version": "14.0.1.0.7",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "school_year", "hezkuntza_res_partner_student_fields",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "data/hezkuntza_country_data.xml",
        "data/hezkuntza_country_state_data.xml",
        "data/hezkuntza_gender_data.xml",
        "data/hezkuntza_language_data.xml",
        "views/hezkuntza_student_import_view.xml",
        "views/hezkuntza_mapping_view.xml",
    ],
    "installable": True,
}
