import os
import subprocess
import sys


def test_no_header_dataset():
    csv_file = os.path.join(os.path.dirname(__file__), "data")
    main_py = os.path.join(os.path.dirname(__file__), '../../../', 'csv_to_ddl', 'main.py')

    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    result = subprocess.run([sys.executable, main_py,
                             '-i', csv_file,
                             '-o', 'testing/no_header/schema_no_header/schema.sql',
                             '-r', 'testing/no_header/schema_no_header/report.json',
                             '-v'], capture_output=True, text=True, env=env, timeout=60)
    print(result.stdout)
    print(result.stderr)
