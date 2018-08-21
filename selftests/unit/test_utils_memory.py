import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from avocado.utils import memory


class UtilsMemoryTest(unittest.TestCase):

    def test_numa_nodes_with_memory(self):
        file_values = [u"0\n", u"1-3", u"0-1,12-14\n"]
        expected_values = [[0], [1, 2, 3], [0, 1, 12, 13, 14]]
        for value, exp in zip(file_values, expected_values):
            with mock.patch('os.path.exists', return_value=True):
                with mock.patch('avocado.utils.genio.read_file',
                                return_value=value):
                    self.assertEqual(memory.numa_nodes_with_memory(), exp)


BUDDY_INFO_RESPONSE = '\n'.join([
    'Node 0, zone      DMA      1      1      0      0      1      1',
    'Node 0, zone    DMA32    987    679   1004   3068   2795   1432',
    'Node 1, zone   Normal   5430   9759   9044   9751  16482   8924',
])


@mock.patch('avocado.utils.memory._get_buddy_info_content', return_value=BUDDY_INFO_RESPONSE)
class UtilsMemoryTestGetBuddyInfo(unittest.TestCase):

    def test_get_buddy_info_simple_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '0'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result[chunk_size], 6418)

    def test_get_buddy_info_less_than_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '<2'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['0'], 6418)
        self.assertEqual(result['1'], 10439)

    def test_get_buddy_info_less_than_equal_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '<=2'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['0'], 6418)
        self.assertEqual(result['1'], 10439)
        self.assertEqual(result['2'], 10048)

    def test_get_buddy_info_greater_than_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '>3'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['4'], 19278)
        self.assertEqual(result['5'], 10357)

    def test_get_buddy_info_greater_than_equal_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '>=3'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['3'], 12819)
        self.assertEqual(result['4'], 19278)
        self.assertEqual(result['5'], 10357)

    def test_get_buddy_info_multiple_chunk_size(self, buddy_info_content_mocked):
        chunk_size = '2 4'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['2'], 10048)
        self.assertEqual(result['4'], 19278)

    def test_get_buddy_info_multiple_chunk_size_filtering_simple(self, buddy_info_content_mocked):
        chunk_size = '>2 <4'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['3'], 12819)

    def test_get_buddy_info_multiple_chunk_size_filtering(self, buddy_info_content_mocked):
        chunk_size = '>=2 <=4'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result['2'], 10048)
        self.assertEqual(result['3'], 12819)
        self.assertEqual(result['4'], 19278)

    def test_get_buddy_info_multiple_chunk_size_filtering_invalid(self, buddy_info_content_mocked):
        chunk_size = '>2 <2'
        result = memory.get_buddy_info(chunk_size)
        self.assertEqual(result, {})

    def test_get_buddy_info_filtering_node(self, buddy_info_content_mocked):
        chunk_size = '0'
        result = memory.get_buddy_info(chunk_size, nodes='1')
        self.assertEqual(result[chunk_size], 5430)

    def test_get_buddy_info_filtering_zone(self, buddy_info_content_mocked):
        chunk_size = '0'
        result = memory.get_buddy_info(chunk_size, zones='DMA32')
        self.assertEqual(result[chunk_size], 987)


if __name__ == '__main__':
    unittest.main()
