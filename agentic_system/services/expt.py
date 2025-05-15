from dotenv import load_dotenv
load_dotenv()

import os

skey = os.environ.get("SERPAPI_KEY")
print(skey)