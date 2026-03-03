import asyncio
import unittest

from app.core import state
from app.services import mitre_mapper, risk_scoring_engine
from app.services.pipeline_orchestrator import process_log


class ServiceTests(unittest.TestCase):
    def setUp(self):
        state.incidents.clear()
        state.cases.clear()
        state.audit_logs.clear()
        state.agent_activity.clear()

    def test_risk_scoring_formula(self):
        result = risk_scoring_engine.score('High', 0.9, 1.2)
        self.assertEqual(result['risk_score'], 81.0)
        self.assertEqual(result['risk_level'], 'High')

    def test_mitre_mapper_known_indicator(self):
        mapped = mitre_mapper.map_mitre(['failed password'])
        self.assertEqual(mapped[0]['technique_id'], 'T1110.001')

    def test_pipeline_creates_incident_and_agent_activity(self):
        incident = asyncio.run(
            process_log('tenant-a', '203.0.113.47', 'Failed password brute force detected', 1.2)
        )
        self.assertTrue(incident['id'].startswith('INC-'))
        self.assertEqual(incident['tenant_id'], 'tenant-a')
        self.assertGreaterEqual(incident['risk_score'], 0)
        self.assertEqual(len(state.incidents), 1)
        self.assertEqual(len(state.agent_activity), 1)


if __name__ == '__main__':
    unittest.main()
