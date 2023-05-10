# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hezkuntza Survey Glue Module",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "survey", "hezkuntza_student_group_importer_company_internships",
    ],
    "excludes": [],
    "data": [
        "views/survey_user_input_line_view.xml",
        "views/survey_user_input_view.xml",
    ],
    "installable": True,
    "autoinstall": True,
}
