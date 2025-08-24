import os
import subprocess
import sys


def test_instacart():
    csv_file = os.path.join(os.path.dirname(__file__), "../datasets/instacart")
    main_py = os.path.join(os.path.dirname(__file__), '../../../', 'csv_to_ddl', 'main.py')

    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    result = subprocess.run([sys.executable, main_py,
                    '-i', csv_file,
                    '-o', 'testing/schema/instacart/schema.sql',
                    '-r', 'testing/schema/instacart/report.json',
                    '-v'],
                   capture_output=True, text=True, env=env, timeout=60)

    print(result.stdout)
    print(result.stderr)
