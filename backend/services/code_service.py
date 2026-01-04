import sys
import subprocess
import tempfile
import os
from typing import Dict, Any

class CodeService:
    """Service for executing Python code safely (Simulation of a sandbox)"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def execute_python(self, code: str) -> Dict[str, Any]:
        """
        Executes Python code and returns the output.
        Note: This is a basic implementation. In a production environment, 
        this should be run in a highly restricted containerized environment.
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            # Execute the code using the current python interpreter
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Clean up the temporary file
            os.unlink(tmp_path)

            if result.returncode == 0:
                return {
                    "status": "success",
                    "output": result.stdout,
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "output": result.stdout,
                    "error": result.stderr
                }

        except subprocess.TimeoutExpired:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return {
                "status": "error",
                "output": "",
                "error": f"Execution timed out after {self.timeout} seconds."
            }
        except Exception as e:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return {
                "status": "error",
                "output": "",
                "error": str(e)
            }

# Singleton instance
code_service = CodeService()
