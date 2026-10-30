import unittest
from ghostqueue.core import predict,triage

class GhostQueueTests(unittest.TestCase):
    def test_model_weights_predict(self):
        self.assertIn(predict('temporary network timeout')['label'],{'retry','review'})
    def test_untrusted_is_quarantined(self):
        self.assertEqual(triage({'id':'x','message':'all fine','trusted':False})['suggested_state'],'quarantine')
    def test_side_effect_requires_review(self):
        self.assertEqual(triage({'message':'job completed with verified receipt','external_side_effect':True})['suggested_state'],'review')
    def test_untrusted_takes_precedence_over_side_effect(self):
        self.assertEqual(triage({'message':'job completed','trusted':False,'external_side_effect':True})['suggested_state'],'quarantine')
    def test_never_executes(self):
        self.assertEqual(triage({'message':'retry network timeout'})['executed_actions'],0)
    def test_confidence_bounded(self):
        self.assertLessEqual(predict('unknown event')['confidence'],1)

if __name__=='__main__':unittest.main()
