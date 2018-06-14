from unittest import TestCase
from broker.common.entity_summary import EntitySummary


class EntitySummaryTest(TestCase):

    def test_add_entity_summary(self):
        entity_summary = EntitySummary()
        entity_summary.breakdown['reanimated_donor'] = {'count': 5}
        entity_summary.breakdown['next_level_seq_protocol'] = {'count': 3}
        entity_summary.breakdown['nanomachine'] = {'count': 1000}
        entity_summary.count = 1008

        another_entity_summary = EntitySummary()
        another_entity_summary.breakdown['reanimated_donor'] = {'count': 11}
        another_entity_summary.breakdown['nanomachine'] = {'count': 2000}
        another_entity_summary.breakdown['micromachine'] = {'count': 40}
        another_entity_summary.count = 2051

        added_together = entity_summary + another_entity_summary
        assert added_together.count == 1008 + 2051

        assert added_together.breakdown['reanimated_donor']['count'] == 16
        assert added_together.breakdown['next_level_seq_protocol']['count'] ==3
        assert added_together.breakdown['nanomachine']['count'] == 3000
        assert added_together.breakdown['micromachine']['count'] == 40

        assert len(added_together.breakdown.items()) == 4

        # assert original summary wasn't modified by the add
        assert entity_summary.count == 1008
        assert len(entity_summary.breakdown.items()) == 3
