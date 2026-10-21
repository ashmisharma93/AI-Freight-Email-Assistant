from pathlib import Path
import pandas as pd
import json

project_root = Path(__file__).resolve().parent.parent
csv_path = project_root/"sample_emails.csv"

df = pd.read_csv(csv_path)
emails = df.to_dict(orient="records")

print(json.dumps(emails, indent=2))
