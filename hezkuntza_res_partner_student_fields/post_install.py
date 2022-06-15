# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import SUPERUSER_ID, api


def activate_hezkuntza_languages(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        activate_basque = env['base.language.install'].create({
            'lang': 'eu_ES',
            'overwrite': True,
        })
        activate_spanish = env['base.language.install'].create({
            'lang': 'es_ES',
            'overwrite': True,
        })
        activate_basque.lang_install()
        activate_spanish.lang_install()
    return
