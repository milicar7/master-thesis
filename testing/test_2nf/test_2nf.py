import csv
import os

from csv_to_ddl.config.config_manager import ConfigManager
from csv_to_ddl.schema_analysis.models.dialects import DataType
from csv_to_ddl.schema_analysis.models.table import TableSpec, ColumnSpec, PrimaryKeySpec, ColumnSizeSpec
from csv_to_ddl.schema_analysis.normalization.second_normal_form import SecondNormalForm


def load_csv_data(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows

def create_table_spec():
    columns = [
        ColumnSpec(name="StudentID", data_type=DataType.VARCHAR, nullable=False, 
                   size_spec=ColumnSizeSpec(max_length=10)),
        ColumnSpec(name="CourseID", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=10)), 
        ColumnSpec(name="StudentName", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=50)),
        ColumnSpec(name="CourseName", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=100)),
        ColumnSpec(name="Grade", data_type=DataType.VARCHAR, nullable=False,
                   size_spec=ColumnSizeSpec(max_length=2)),
        ColumnSpec(name="Credits", data_type=DataType.INTEGER, nullable=False)
    ]

    primary_key = PrimaryKeySpec(
        columns=["StudentID", "CourseID"],
        key_type="composite"
    )
    
    return TableSpec(
        name="student_course",
        columns=columns,
        primary_key=primary_key
    )

def test_second_normal_form():
    csv_path = os.path.join(os.path.dirname(__file__), "test_2nf_data.csv")
    headers, rows = load_csv_data(csv_path)

    table_spec = create_table_spec()
    
    config = ConfigManager().get_normalization_config()
    analyzer = SecondNormalForm(config)
    
    suggestions = analyzer.check("student_course", headers, rows, table_spec)

    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"Violation #{i}:")
            print(f"  Type: {suggestion.suggestion_type}")
            print(f"  Description: {suggestion.description}")
            print(f"  Confidence: {suggestion.confidence:.1%}")
            print()
    else:
        print("No 2NF violations detected.")
    
    print("Expected violations:")
    print("- StudentName should depend only on StudentID (not CourseID)")
    print("- CourseName should depend only on CourseID (not StudentID)")
    print("- Credits should depend only on CourseID (not StudentID)")

if __name__ == "__main__":
    test_second_normal_form()