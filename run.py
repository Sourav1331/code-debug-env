import sys
import os

# Add project root and OpenEnv to path
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "OpenEnv"))
sys.path.insert(0, os.path.join(BASE, "OpenEnv", "src"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("server.app:app", host="127.0.0.1", port=7860, reload=True)