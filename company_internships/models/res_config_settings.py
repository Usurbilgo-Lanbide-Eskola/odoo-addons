# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
import re


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_stage_ids = fields.Many2many(comodel_name="crm.stage", )


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        stage_ids_str = param.get_param('company_internships.crm_stage_ids', default='[]')
        try:
            stage_ids = eval(stage_ids_str) if stage_ids_str else []
        except:
            stage_ids = []
        res.update(crm_stage_ids=[(6, 0, stage_ids)])
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('company_internships.crm_stage_ids', str(self.crm_stage_ids.ids))
        
    def get_crm_stage_ids(self):
        param = self.env['ir.config_parameter'].sudo()
        stage_ids_str = param.get_param('company_internships.crm_stage_ids', default='[]')
        try:
            return eval(stage_ids_str) if stage_ids_str else []
        except:
            return []