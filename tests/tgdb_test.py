from tgdb import __init__
import unittest
import shutil

TEMPDIR = "/tmp/TestDBDirectory"

if __name__ == '__main__':
    unittest.main()


class TestUsers(unittest.TestCase):
    def setUp(self) -> None:
        self.db = __init__.TGDatabase(TEMPDIR, {"password": "12345"}, {"name": "Ivan", "age": 40})

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(TEMPDIR)

    def test_user(self):
        self.db.set(123, "name", "Sascha")
        cur_pass = self.db.get(123, "name")
        self.assertEqual(cur_pass, "Sascha")

        user = self.db.get_user(123)
        user["age"] = 30
        user["country"] = "Deutschland"
        self.db.overwrite_user(123, user)
        self.assertEqual(self.db.get(123, "age"), 30)
        self.assertEqual(self.db.get(123, "country"), "Deutschland")

    def test_config(self):
        self.db.config_set("password", "qwerrr")
        self.assertEqual(self.db.config_get("password"), "qwerrr")