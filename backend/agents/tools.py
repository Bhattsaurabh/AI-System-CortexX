import os
import subprocess
from langchain_core.tools import tool
from pydantic import BaseModel, Field

def get_agent_tools(project_dir: str):
    """Returns a list of tools bound to the specific project directory."""
    
    # Ensure the project directory exists
    if not os.path.exists(project_dir):
        os.makedirs(project_dir, exist_ok=True)
    
    class WriteFileInput(BaseModel):
        filename: str = Field(description="The name of the file to write. Can include relative directories.")
        content: str = Field(description="The complete code or content to write to the file.")

    @tool("write_file", args_schema=WriteFileInput)
    def write_file(filename: str, content: str) -> str:
        """Writes content to a file in the project directory."""
        try:
            # Prevent directory traversal attacks
            safe_path = os.path.abspath(os.path.join(project_dir, filename))
            if not safe_path.startswith(os.path.abspath(project_dir)):
                return "Error: Cannot write outside the project directory."
                
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {filename}"
        except Exception as e:
            return f"Failed to write file: {str(e)}"

    class RunCommandInput(BaseModel):
        command: str = Field(description="The terminal command to execute.")

    @tool("run_command", args_schema=RunCommandInput)
    def run_command(command: str) -> str:
        """Executes a terminal command in the project directory and returns the output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
                
            if not output.strip():
                return f"Command executed successfully with exit code {result.returncode} (No output)"
                
            # Truncate very long outputs to prevent blowing up the LLM context
            if len(output) > 5000:
                output = output[:2500] + "\n...[TRUNCATED]...\n" + output[-2500:]
                
            return output
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 60 seconds."
        except Exception as e:
            return f"Failed to execute command: {str(e)}"

    class ReadFileInput(BaseModel):
        filename: str = Field(description="The name of the file to read. Can include relative directories.")

    @tool("read_file", args_schema=ReadFileInput)
    def read_file(filename: str) -> str:
        """Reads and returns the content of a file in the project directory."""
        try:
            safe_path = os.path.abspath(os.path.join(project_dir, filename))
            if not safe_path.startswith(os.path.abspath(project_dir)):
                return "Error: Cannot read outside the project directory."
            
            if not os.path.exists(safe_path):
                return f"Error: File {filename} does not exist."
                
            with open(safe_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Failed to read file: {str(e)}"

    class EditFileInput(BaseModel):
        filename: str = Field(description="The name of the file to edit.")
        old_string: str = Field(description="The exact string in the file to replace. Must be an exact match including whitespace.")
        new_string: str = Field(description="The new string to replace it with.")

    @tool("edit_file", args_schema=EditFileInput)
    def edit_file(filename: str, old_string: str, new_string: str) -> str:
        """Edits an existing file by replacing an exact string with a new string."""
        try:
            safe_path = os.path.abspath(os.path.join(project_dir, filename))
            if not safe_path.startswith(os.path.abspath(project_dir)):
                return "Error: Cannot edit outside the project directory."
                
            if not os.path.exists(safe_path):
                return f"Error: File {filename} does not exist."
                
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if old_string not in content:
                return "Error: The exact old_string was not found in the file. Check whitespace and formatting."
                
            new_content = content.replace(old_string, new_string, 1)
            
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return f"Successfully edited {filename} (Replaced 1 occurrence of target string)."
        except Exception as e:
            return f"Failed to edit file: {str(e)}"

    return [write_file, run_command, read_file, edit_file]
