from unittest import TestCase, skip
from wenuclient import Entity
from phony import Client

class TestEntity(TestCase):
    def setUp(self):
        self.reqres = {
            'http://example.com/table': {"_items": [
                {'name': 'value', '_id': 20},
                {'name': 'value', '_id': 22},
            ]},
            'http://example.com/table/20': {"_items": [{'name': 'value', '_id': 20}]},
            'http://example.com/table/22': {"_items": [{'name': 'value', '_id': 22}]},
            'http://example.com/measurement': {"_items": [{'name': 'value', '_id': 20}]},
        }
        client = Client('http://example.com', self.reqres)

        self.Table = Entity.spawn_subclass('Table', 'table', client)
        self.Measurement = Entity.spawn_subclass('Measurement', 'measurement', client)
        self.table_elements = self.Table.list()
        self.measurement_elements = self.Table.list()

    def test_table_fields_are_instance_attributes(self):
        self.assertEqual(self.table_elements[0].name, 'value')

    def test_not_everthing_is_an_attribute(self):
        def should_fail():
            self.table_elements[0].not_a_field
        self.assertRaises(AttributeError, should_fail)

    def test_list_returns_a_sequence_of_instances(self):
        elements = self.Table.list()
        self.assertIsInstance(elements, list)
        self.assertEqual(len(elements), 2)
        self.assertIsInstance(elements[0], self.Table)

    def test_get_by_id_is_not_implemented_for_measurement(self):
        def should_fail():
            self.Measurement.get_by_id(20)
        self.assertRaises(AssertionError, should_fail)

    def test_get_by_id_returns_something_if_it_exists(self):
        self.assertIsInstance(self.Table.get_by_id(20), self.Table)

    @skip
    def test_get_by_id_fails_gracefully_if_not_found(self):
        self.assertIsNone(self.Table.get_by_id(10))
