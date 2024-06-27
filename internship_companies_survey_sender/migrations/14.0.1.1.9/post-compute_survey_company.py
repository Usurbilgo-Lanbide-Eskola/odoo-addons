import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    cr.execute(
        """
        UPDATE survey_survey s
        SET company_id = (SELECT student_company_id FROM 
        school_year_historical y WHERE y.school_year_id = s.school_year_id 
        and s.instance_id = y.student_company_id LIMIT 1)
        WHERE company_id is null and survey_template = false and 
            survey_type = (SELECT id FROM survey_type where model_id = (
            SELECT id FROM 
            ir_model WHERE 
            model= 
            'res.partner'))
        """
    )