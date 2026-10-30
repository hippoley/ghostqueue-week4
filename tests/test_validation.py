import unittest
from ghostqueue.core import predict, triage

class ValidationTests(unittest.TestCase):
    def test_non_object_rejected(self):
        with self.assertRaisesRegex(ValueError, 'JSON object'):
            triage(['not', 'an', 'event'])

    def test_missing_message_rejected(self):
        with self.assertRaisesRegex(ValueError, 'non-empty'):
            triage({'id':'missing'})

    def test_blank_message_rejected(self):
        with self.assertRaises(ValueError):
            triage({'message':'  '})

    def test_long_message_rejected(self):
        with self.assertRaisesRegex(ValueError, '10000'):
            triage({'message':'x'*10001})

    def test_boolean_strings_rejected(self):
        for flag in ('trusted','external_side_effect','requires_approval'):
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, 'boolean'):
                triage({'message':'network timeout',flag:'false'})

    def test_non_string_message_rejected(self):
        with self.assertRaises(ValueError):
            triage({'message':None})

    def test_bad_event_id_rejected(self):
        with self.assertRaises(ValueError):
            triage({'message':'network timeout','id':{'nested':'bad'}})

    def test_predict_rejects_non_string(self):
        with self.assertRaises(ValueError):
            predict(None)

    def test_valid_event_still_advisory(self):
        result=triage({'id':'case','message':'temporary network timeout','trusted':False})
        self.assertEqual(result['suggested_state'],'quarantine')
        self.assertEqual(result['executed_actions'],0)

    def test_boolean_event_id_rejected(self):
        with self.assertRaisesRegex(ValueError, 'event.id'):
            triage({'message':'temporary network timeout','id':True})

    def test_blank_event_id_rejected(self):
        with self.assertRaisesRegex(ValueError, 'event.id'):
            triage({'message':'temporary network timeout','id':'   '})
