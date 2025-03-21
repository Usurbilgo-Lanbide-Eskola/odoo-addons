# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
import re


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    crm_stage_ids = fields.Many2many(comodel_name="crm.stage")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(crm_stage_ids=[(6,0,self.get_m2m_ids(self.env[
            'ir.config_parameter'].sudo().get_param(
            'company_internships.crm_stage_ids', default=False)))])
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('company_internships.crm_stage_ids',
                        self.crm_stage_ids.ids)
        
    def get_crm_stage_ids(self):
        stages = self.env['ir.config_parameter'].sudo().get_param(
            'company_internships.crm_stage_ids', default=False)
        return self.get_m2m_ids(stages)

    def get_m2m_ids(self, m2m_str):
        res = re.findall(r"\((.*?)\)", m2m_str)
        if res:
            res_ids = [int(i) for i in res[0].split(",")]
        return res_ids or []
