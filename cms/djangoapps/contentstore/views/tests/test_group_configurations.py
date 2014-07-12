"""
Group Configuration Tests.
"""
import json
import mock
from contentstore.utils import reverse_course_url
from contentstore.tests.utils import CourseTestCase
from xmodule.partitions.partitions import Group, UserPartition


GROUP_CONFIGURATION_JSON = {
    u'name': u'Test name',
    u'description': u'Test description',
}


class MockedUuid(object):
    """
    Mock UUID class.
    """
    def __init__(self):
        self.generator = self.next_number()

    @property
    def int(self):
        """
        Return next number.
        """
        return self.generator.next()

    def next_number(self):
        """
        Generate next number.
        """
        num = long('{0:0<39d}'.format(1))
        while True:
            yield num
            num += long('{0:0<39d}'.format(1))


class GroupConfigurationsBaseTestCase(object):
    """
    Base test cases for the group configurations.
    """
    def setUp(self):  # pylint: disable=E1101
        """
        Set up a url and group configuration content for tests.
        """
        super(GroupConfigurationsBaseTestCase, self).setUp()
        patcher = mock.patch('uuid.uuid4', return_value=MockedUuid())
        self.patched_uuid4 = patcher.start()
        self.addCleanup(patcher.stop)

    def test_required_fields_are_absent(self):
        """
        Test required fields are absent.
        """
        bad_jsons = [
            # must have description of the configuration
            {
                u'name': 'Test Name',
                u'groups': [
                    {u'name': u'Group A'},
                    {u'name': u'Group B'},
                ],
            },
            # must have name of the configuration
            {
                u'description': 'Test description',
                u'groups': [
                    {u'name': u'Group A'},
                    {u'name': u'Group B'},
                ],
            },
            # must have at least two groups
            {
                u'name': u'Test name',
                u'description': u'Test description',
                u'groups': [
                    {u'name': u'Group A'},
                ],
            },
            # an empty json
            {},
        ]

        for bad_json in bad_jsons:
            response = self.client.post(
                self._url(),
                data=json.dumps(bad_json),
                content_type="application/json",
                HTTP_ACCEPT="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 400)
            self.assertNotIn("Location", response)
            content = json.loads(response.content)
            self.assertIn("error", content)

    def test_invalid_json(self):
        """
        Test invalid json handling.
        """
        # No property name.
        invalid_json = "{u'name': 'Test Name', []}"

        response = self.client.post(
            self._url(),
            data=invalid_json,
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("Location", response)
        content = json.loads(response.content)
        self.assertIn("error", content)


class GroupConfigurationsListHandlerTestCase(GroupConfigurationsBaseTestCase, CourseTestCase):  # pylint: disable=E1101
    """
    Test cases for group_configurations_list_handler.
    """

    def setUp(self):
        """
        Set up GroupConfigurationsListHandlerTestCase.
        """
        super(GroupConfigurationsListHandlerTestCase, self).setUp()

    def _url(self):
        """
        Return url for the handler.
        """
        return reverse_course_url('group_configurations_list_handler', self.course.id)

    def test_can_retrieve_html(self):
        """
        Check that the group configuration index page responds correctly.
        """
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertIn('New Group Configuration', response.content)

    def test_unsupported_http_accept_header(self):
        """
        Test if not allowed header present in request.
        """
        response = self.client.get(
            self._url(),
            HTTP_ACCEPT="text/plain",
        )
        self.assertEqual(response.status_code, 406)

    def test_can_retrieve_collection_of_configurations(self):
        """
        Check that the group configuration lists all configurations.
        """
        self.course.user_partitions = [
            UserPartition(1, 'Test name', 'Test description', [Group(0, 'Group A'), Group(1, 'Group B')]),
            UserPartition(2, 'Test name 2', 'Test description 2', [Group(0, 'Group 0'), Group(1, 'Group 1'), Group(2, 'Group 2')]),
        ]
        self.save_course()

        expected = [
            {
                u'id': 1,
                u'name': u'Test name',
                u'description': u'Test description',
                u'groups': [
                    {u'id': 0, u'name': u'Group A'},
                    {u'id': 1, u'name': u'Group B'},
                ],
            },
            {
                u'id': 2,
                u'name': u'Test name 2',
                u'description': u'Test description 2',
                u'groups': [
                    {u'id': 0, u'name': u'Group 0'},
                    {u'id': 1, u'name': u'Group 1'},
                    {u'id': 2, u'name': u'Group 2'},
                ],
            },
        ]

        response = self.client.get(
            self._url(),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        content = json.loads(response.content)
        self.assertItemsEqual(content, expected)

    def test_can_create_group_configuration(self):
        """
        Test that you can create a group configuration.
        """
        expected = {
            u'id': 10000000,
            u'description': u'Test description',
            u'name': u'Test name',
            u'groups': [
                {u'id': 0, u'name': u'Group A'},
                {u'id': 1, u'name': u'Group B'},
            ],
        }
        response = self.client.post(
            self._url(),
            data=json.dumps(GROUP_CONFIGURATION_JSON),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Location", response)
        content = json.loads(response.content)
        self.assertEqual(content, expected)


class GroupConfigurationsDetailHandlerTestCase(GroupConfigurationsBaseTestCase, CourseTestCase):  # pylint: disable=E1101
    """
    Test cases for group_configurations_detail_handler.
    """

    ID = int(str(MockedUuid().int)[:8])

    def setUp(self):
        """
        Set up GroupConfigurationsDetailHandlerTestCase.
        """
        super(GroupConfigurationsDetailHandlerTestCase, self).setUp()

        self.course.user_partitions = [
            UserPartition(self.ID, 'Test name', 'Test description', [Group(0, 'Group A'), Group(1, 'Group B'), Group(2, 'Group C')]),
        ]
        self.save_course()

    def _url(self, cid=None):
        """
        Return url for the handler.
        """
        cid = cid if cid is not None else self.ID
        return reverse_course_url(
            'group_configurations_detail_handler',
            self.course.id,
            kwargs={'group_configuration_id': cid},
        )

    def test_can_create_new_group_configuration_if_it_is_not_exist(self):
        """
        PUT new group configuration when no configurations exist in the course.
        """
        # Make no partitions in course.
        self.course.user_partitions = []
        self.save_course()

        expected = {
            u'id': self.ID,
            u'name': u'Test name',
            u'description': u'Test description',
            u'groups': [
                {u'id': 0, u'name': u'Group A'},
                {u'id': 1, u'name': u'Group B'},
            ],
        }

        response = self.client.put(
            self._url(),
            data=json.dumps(GROUP_CONFIGURATION_JSON),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        content = json.loads(response.content)
        self.assertEqual(content, expected)

    def test_can_edit_group_configuration(self):
        """
        Edit group configuration and check its id and modified fields.
        """
        expected = {
            u'id': self.ID,
            u'name': u'New Test name',
            u'description': u'New Test description',
            u'groups': [
                {u'id': 0, u'name': u'Group A'},
                {u'id': 1, u'name': u'Group B'},
            ],
        }
        response = self.client.put(
            self._url(),
            data=json.dumps(expected),
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        content = json.loads(response.content)
        self.assertEqual(content, expected)

    def test_can_get_group_configuration(self):
        """
        Group configuration with appropriate id is present in the course.
        """
        expected = {
            u'id': self.ID,
            u'name': u'Test name',
            u'description': u'Test description',
            u'groups': [
                {u'id': 0, u'name': u'Group A'},
                {u'id': 1, u'name': u'Group B'},
                {u'id': 2, u'name': u'Group C'},
            ],
        }
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, expected)

    def test_get_404_if_group_configuration_does_not_exist(self):
        """
        Group configuration is not present in the course.
        """
        response = self.client.get(self._url(cid=999))
        self.assertEqual(response.status_code, 404)
