# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_neurological.tests.common \
    import neurological_fixtures
from openerp.tests.common import SingleTransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetReportData(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestGetReportData, cls).setUpClass()
        cls.test_utils = cls.env['nh.clinical.test_utils']
        cls.test_utils.admit_and_place_patient()
        cls.test_utils.copy_instance_variables(cls)

        cls.nurse = cls.test_utils.nurse
        cls.nurse_name = 'Hilda Garde'
        cls.nurse.name = cls.nurse_name

        cls.report_wizard_model = \
            cls.env['nh.clinical.observation_report_wizard']
        cls.report_model = cls.env['report.nh.clinical.observation_report']

        cls.test_utils.create_and_complete_neuro_obs(
            cls.patient.id, neurological_fixtures.SAMPLE_DATA, user=cls.nurse
        )
        cls.test_utils.create_and_complete_neuro_obs(
            cls.patient.id, neurological_fixtures.SAMPLE_DATA, user=cls.nurse
        )
        cls.test_utils.create_and_complete_neuro_obs(
            cls.patient.id, neurological_fixtures.SAMPLE_DATA, user=cls.nurse
        )
        cls.datetime_start = datetime.now() - timedelta(days=2)
        cls.datetime_end = datetime.now()

        cls.report_wizard = cls.report_wizard_model.create({
            'start_time': cls.datetime_start.strftime(DTF),
            'end_time': cls.datetime_end.strftime(DTF)
        })
        cls.report_wizard.spell_id = cls.spell.id

        cls.report_data = \
            cls.report_model.get_report_data(cls.report_wizard)
        cls.neurological_obs_data = cls.report_data['neurological']

    def get_field_values(self, field_name):
        return [data['values'][field_name] for data in
                self.neurological_obs_data]

    def get_user_values(self):
        return [data['user'] for data in self.neurological_obs_data]

    def test_returns_dict_with_neurological_key_with_list_value(self):
        self.assertTrue('neurological' in self.report_data)
        self.assertTrue(type(self.report_data['neurological']) is list)

    def test_valid_date_value(self):
        pass

    def test_eyes_not_testable(self):
        field_values = self.get_field_values('eyes')
        for field_value in field_values:
            self.assertEqual('NT', field_value)

    def test_pupil_right_size_not_observable(self):
        field_values = self.get_field_values('pupil_right_size')
        for field_value in field_values:
            self.assertEqual('NO', field_value)

    def test_user_has_name_and_surname_of_user_who_submitted_the_obs(self):
        field_values = self.get_user_values()
        for field_value in field_values:
            self.assertEqual(self.nurse_name, field_value)

    def test_returns_dict_with_neurological_data(self):
        """
        Test that get_report_data returns a key with json representation of
        activities
        """
        report_data = self.report_data
        self.assertTrue('neurological' in report_data)
        self.assertTrue(type(report_data['neurological']) is list)
