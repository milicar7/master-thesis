import csv
import os

from config.config_manager import ConfigManager
from config.default_config import NormalizationConfig
from csv_to_ddl.models.dialects import DataType
from csv_to_ddl.models.table import TableSpec, ColumnSpec, PrimaryKeySpec, ColumnSizeSpec
from csv_to_ddl.normalization.third_normal_form import ThirdNormalForm


def load_csv_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows


def create_student_table_spec():
    columns = [
        ColumnSpec(name="StudentID", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=10)),
        ColumnSpec(name="Name", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=100)),
        ColumnSpec(name="CourseID", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=10)),
        ColumnSpec(name="CourseName", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=100)),
        ColumnSpec(name="Instructor", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=100))
    ]

    primary_key = PrimaryKeySpec(
        columns=["StudentID", "CourseID"],
        key_type="composite",
        confidence=1.0,
        reasoning="StudentID and CourseID together uniquely identify enrollment records"
    )

    return TableSpec(
        name="student_enrollment",
        columns=columns,
        primary_key=primary_key
    )


def create_3nf_compliant_table_spec():
    columns = [
        ColumnSpec(name="StudentID", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=10)),
        ColumnSpec(name="CourseID", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=10)),
        ColumnSpec(name="Grade", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=2)),
        ColumnSpec(name="EnrollmentDate", data_type=DataType.DATE, nullable=False)
    ]

    primary_key = PrimaryKeySpec(
        columns=["StudentID", "CourseID"],
        key_type="composite",
        confidence=1.0,
        reasoning="StudentID and CourseID together uniquely identify enrollment records"
    )

    return TableSpec(
        name="enrollment_only",
        columns=columns,
        primary_key=primary_key
    )


def test_third_normal_form_violations():
    csv_path = os.path.join(os.path.dirname(__file__), "test_3nf_data.csv")
    headers, rows = load_csv_data(csv_path)

    table_spec = create_student_table_spec()
    tables_data = {"student_enrollment": rows}
    tables_headers = {"student_enrollment": headers}

    config = ConfigManager().get_normalization_config()
    analyzer = ThirdNormalForm(config)
    suggestions = analyzer.check(
        table_name="student_enrollment",
        table_spec=table_spec,
        tables_data=tables_data,
        tables_headers=tables_headers
    )

    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"Violation #{i}:")
            print(f"  Type: {suggestion.suggestion_type}")
            print(f"  Description: {suggestion.description}")
            print(f"  Confidence: {suggestion.confidence:.1%}")
            print()
    else:
        print("No 3NF violations detected.")

    print("Expected violations:")
    print("- Instructor depends on CourseName, creating transitive dependency")
    print("- CourseName → Instructor (transitive through primary key)")


if __name__ == "__main__":
     test_third_normal_form_violations()