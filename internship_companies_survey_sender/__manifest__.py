# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Internship Survey Sender",
    "version": "14.0.1.0.2",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "survey_model_instance_link", "company_internships"
    ],
    "excludes": [],
    "data": [
        "data/answer_bundle_email_template.xml",
        "security/ir.model.access.csv",
        "views/res_partner_view.xml",
        "wizard/send_company_internships_view.xml",
    ],
    "installable": True,
}
