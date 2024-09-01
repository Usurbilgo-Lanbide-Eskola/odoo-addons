{
    "name": "Hezkuntza Google Workspace",
    "version": "14.0.1.0.1",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "hezkuntza_student_group_importer"
    ],
    "external_dependencies": {"python": ["google-api-python-client",
                                         "google-auth-httplib2", "google-auth-oauthlib"]},
    "excludes": [],
    "data": [
        "views/hezkuntza_student_group_view.xml",
        "views/res_config_settings_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}