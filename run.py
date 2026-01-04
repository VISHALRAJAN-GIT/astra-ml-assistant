import uvicorn
import os
import sys

# Add backend to path so services can be imported
sys.path.append(os.path.join(os.getcwd(), 'backend'))

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
