import os


def load_env_file(file_path: str):
    with open(file_path) as f:
        for line in f:
            line = line.replace('\n', '')

            if not line or line.startswith('#'):
                continue

            if line.lower().startswith('export '):
                key, value = line.replace('export ', '', 1).strip().split('=', 1)
            else:
                key, value = line.strip().split('=', 1)

            os.environ[key] = value
