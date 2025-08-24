import os
import subprocess
import sys


def test_2nf_no_header():
    csv_file = os.path.join(os.path.dirname(__file__), "test_nf_data_no_header.csv")
    main_py = os.path.join(os.path.dirname(__file__), '../../../', 'csv_to_ddl', 'main.py')

    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    result = subprocess.run([sys.executable, main_py,
                             '-i', csv_file,
                             '-o', 'testing/no_header/nf_no_header/schema.sql',
                             '-r', 'testing/no_header/nf_no_header/report.json',
                             '-v'], capture_output=True, text=True, env=env, timeout=60)
    print("Expected violations:")
    print("- column_3 should depend only on column_1 (not column_2)")
    print("- column_4 should depend only on column_2 (not column_1)")
    print("- column_6 should depend only on column_2 (not column_1)")

    print(result.stdout)
    print(result.stderr)