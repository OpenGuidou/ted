import unittest
from services.TEDGenerator import TEDGenerator

# -------------------------------------------------------------------------------------------
# Unit test class
# -------------------------------------------------------------------------------------------
class TestTedGenerator(unittest.TestCase):
    def test_run_generation(self):
        ted_generator = TEDGenerator()
        self.assertIsNone(ted_generator.run_generation(None, None, None, None))

    def test_get_file_extensions(self):
        ted_generator = TEDGenerator()
        self.assertIsNone(ted_generator.get_file_extensions())

    def test_get_text_format(self):
        ted_generator = TEDGenerator()
        self.assertIsNone(ted_generator.get_text_format())

    def test_get_branch_name(self):
        ted_generator = TEDGenerator()
        self.assertIsNone(ted_generator.get_branch_name())

    def test_get_commit_message(self):
        ted_generator = TEDGenerator()
        self.assertIsNone(ted_generator.get_commit_message())

# -------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
