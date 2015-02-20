# Copyright 2015 Deutsche Telekom AG
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""Test of Volume Test Manager for Manila."""
import datetime

import ddt
import mock

from manila import context
from manila import db
from manila.share import share_types
from manila import test


@ddt.ddt
class ShareTypesTestCase(test.TestCase):

    fake_type = {
        'test': {
            'created_at': datetime.datetime(2015, 1, 22, 11, 43, 24),
            'deleted': '0',
            'deleted_at': None,
            'extra_specs': {},
            'id': u'fooid-1',
            'name': u'test',
            'updated_at': None
        }
    }
    fake_type_w_extra = {
        'test_with_extra': {
            'created_at': datetime.datetime(2015, 1, 22, 11, 45, 31),
            'deleted': '0',
            'deleted_at': None,
            'extra_specs': {u'gold': u'True'},
            'id': u'fooid-2',
            'name': u'test_with_extra',
            'updated_at': None
        }
    }

    fake_types = dict(fake_type.items() + fake_type_w_extra.items())

    def setUp(self):
        super(ShareTypesTestCase, self).setUp()
        self.context = context.get_admin_context()

    @ddt.data({}, fake_type, fake_type_w_extra, fake_types)
    def test_get_all_types(self, share_type):
        self.mock_object(db,
                         'share_type_get_all',
                         mock.Mock(return_value=share_type))
        returned_type = share_types.get_all_types(self.context)
        self.assertItemsEqual(share_type, returned_type)

    def test_get_all_types_filter(self):
        share_type = self.fake_type_w_extra
        search_filter = {"extra_specs": {"gold": "True"}}
        self.mock_object(db,
                         'share_type_get_all',
                         mock.Mock(return_value=share_type))
        returned_type = share_types.get_all_types(self.context,
                                                  search_opts=search_filter)
        self.assertItemsEqual(share_type, returned_type)
        search_filter = {"extra_specs": {"gold": "False"}}
        returned_type = share_types.get_all_types(self.context,
                                                  search_opts=search_filter)
        self.assertEqual({}, returned_type)

    def test_get_share_type_extra_specs(self):
        share_type = self.fake_type_w_extra['test_with_extra']
        self.mock_object(db,
                         'share_type_get',
                         mock.Mock(return_value=share_type))
        id = share_type['id']
        extra_spec = share_types.get_share_type_extra_specs(id, key='gold')
        self.assertEqual(share_type['extra_specs']['gold'], extra_spec)
        extra_spec = share_types.get_share_type_extra_specs(id)
        self.assertEqual(share_type['extra_specs'], extra_spec)

    def test_share_types_diff(self):
        share_type1 = self.fake_type['test']
        share_type2 = self.fake_type_w_extra['test_with_extra']
        expeted_diff = {'extra_specs': {u'gold': (None, u'True')}}
        self.mock_object(db,
                         'share_type_get',
                         mock.Mock(side_effect=[share_type1, share_type2]))
        (diff, equal) = share_types.share_types_diff(self.context,
                                                     share_type1['id'],
                                                     share_type2['id'])
        self.assertFalse(equal)
        self.assertEqual(expeted_diff, diff)

    def test_share_types_diff_equal(self):
        share_type = self.fake_type['test']
        self.mock_object(db,
                         'share_type_get',
                         mock.Mock(return_value=share_type))
        (diff, equal) = share_types.share_types_diff(self.context,
                                                     share_type['id'],
                                                     share_type['id'])
        self.assertTrue(equal)