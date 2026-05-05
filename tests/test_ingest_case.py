import os
import unittest
from unittest.mock import patch
import io
import shutil
from scripts.ingest_case import get_next_case_info, slugify, ingest_case

class TestIngestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary cases directory for testing
        self.test_dir = 'test_cases'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.test_readme = 'test_README.md'
        with open(self.test_readme, 'w', encoding='utf-8') as f:
            f.write("# Index\n\n| ID | Title | Status | Trigger |\n|---|---|---|---|\n| 000 | Bootstrap | ✅ | Initial |\n")

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_readme):
            os.remove(self.test_readme)

    def test_slugify(self):
        self.assertEqual(slugify("Hello World!"), "hello-world")
        self.assertEqual(slugify("가나다 ABC"), "가나다-abc")
        self.assertEqual(slugify("Case [123] Test"), "case-123-test")

    @patch('scripts.ingest_case.os.listdir')
    @patch('scripts.ingest_case.os.path.exists')
    def test_get_next_case_info_empty(self, mock_exists, mock_listdir):
        mock_exists.return_value = True
        mock_listdir.return_value = []
        next_id, next_id_str = get_next_case_info()
        self.assertEqual(next_id, 0)
        self.assertEqual(next_id_str, '000')

    @patch('scripts.ingest_case.os.listdir')
    @patch('scripts.ingest_case.os.path.exists')
    def test_get_next_case_info_increment(self, mock_exists, mock_listdir):
        mock_exists.return_value = True
        mock_listdir.return_value = ['000-bootstrap.md', '001-test.md']
        next_id, next_id_str = get_next_case_info()
        self.assertEqual(next_id, 2)
        self.assertEqual(next_id_str, '002')

if __name__ == '__main__':
    unittest.main()
