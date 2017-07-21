from unittest import TestCase, skip
from wenuclient import Entity
from phony import Client
import mock

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
            'http://example.com/table?where={"name": "something"}': {"_items": [
                {'name': 'something', '_id': 23},
                {'name': 'something', '_id': 25},
            ]},
            'http://example.com/table?where={"_id": 20}': {"_items": [{'name': 'value', '_id': 20},
            ]},
            'http://example.com/table?where={"_id": 222222}': {"_items": []},


        }
        self.client = Client('http://example.com', self.reqres)

        self.Table = Entity.spawn_subclass('Table', 'table', self.client)
        self.Measurement = Entity.spawn_subclass(
            'Measurement',
            'measurement',
            self.client
        )
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

    @skip('Verificar como lo usan las implementaciones antes de modificarlo')
    def test_get_by_id_fails_gracefully_if_not_found(self):
        self.assertIsNone(self.Table.get_by_id(10))

    @skip('Decidir si usar listas o generators')
    def test_where_returns_all_matched_in_a_sequence_of_objects(self):
        elements = self.Table.where(name='something')
        self.assertIsInstance(elements, list)
        self.assertEqual(len(elements), 2)
        self.assertIsInstance(elements[0], self.Table)

    @skip('Decidir si usar listas o generators')
    def test_where_returns_an_empty_sequence_if_no_match(self):
        elements = self.Table.where(name='inexistentstuff')
        self.assertIsInstance(elements, list)
        self.assertEqual(len(elements), 0)

    @skip('Decidir si usar listas o generators')
    def test_embedded_returns_all_matched_in_a_sequence_of_objects(self):
        elements = self.Table.embedded(name='something')
        self.assertIsInstance(elements, list)
        self.assertEqual(len(elements), 2)
        self.assertIsInstance(elements[0], self.Table)

    @skip('Decidir si usar listas o generators')
    def test_embedded_returns_an_empty_sequence_if_no_match(self):
        elements = self.Table.embedded(name='inexistentstuff')
        self.assertIsInstance(elements, list)
        self.assertEqual(len(elements), 0)

    def test_first_where_returns_only_one_match(self):
        match = self.Table.first_where(_id=20)
        self.assertIsInstance(match, self.Table)

    def test_first_where_returns_none_if_no_match(self):
        match = self.Table.first_where(_id=222222)
        self.assertIsNone(match)

    def test_regular_fields_discards_fields_starting_with_underscore(self):
        fields = self.table_elements[0].regular_fields()
        self.assertNotIn('_id', fields)
        self.assertIn('name', fields)

    def test_remove_generates_a_delete_http_request_with_the_correct_url(self):
        self.client.delete = mock.MagicMock(return_value=None)
        self.table_elements[0].remove()
        self.client.delete.assert_called_with('table/20')

    def test_create_generates_a_post_http_request_with_the_correct_url_and_json_message(self):
        self.client.post = mock.MagicMock(return_value={})
        self.table_elements[0].create()
        # post has been called
        self.client.post.assert_called()
        # First positional argument is the url
        self.assertEqual(self.client.post.call_args[0][0], 'table')
        # json is a keyword argument
        self.assertIn('json', self.client.post.call_args[1])
        # post was called with the correct ID
        self.assertEqual(self.client.post.call_args[1]['json']['_id'], 20)

    def test_create_updates_the_fields_of_the_instance(self):
        self.client.post = mock.MagicMock(return_value={'_id': 42, 'name': 'newname'})
        self.table_elements[0].create()
        self.assertEqual(self.table_elements[0]._id, 42)
        self.assertEqual(self.table_elements[0].name, 'newname')

    def test_save_generates_a_put_http_request_with_the_correct_url_and_json_message(self):
        self.client.put = mock.MagicMock(return_value={})
        new_element = self.Table(_id=42, name='x', _etag='abc')
        new_element.save()
        # put has been called
        self.client.put.assert_called()
        # First positional argument is the url
        self.assertEqual(self.client.put.call_args[0][0], 'table/42')
        # json is a keyword argument
        self.assertEqual(self.client.put.call_args[1]['json'], {'name': 'x'})
        # etag is a keyword argument
        self.assertEqual(self.client.put.call_args[1]['etag'], 'abc')
