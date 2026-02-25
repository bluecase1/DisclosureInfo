import unittest

from sqlalchemy import create_engine

from disclosureinfo.models import Base


class ModelsSchemaTest(unittest.TestCase):
    def test_models_import_and_metadata_available(self) -> None:
        self.assertIsNotNone(Base.metadata)

    def test_sqlite_create_all(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        expected_tables = {
            "disclosures",
            "disclosure_details",
            "classifications",
            "extracted_fields",
        }
        self.assertTrue(expected_tables.issubset(set(Base.metadata.tables.keys())))


if __name__ == "__main__":
    unittest.main()
