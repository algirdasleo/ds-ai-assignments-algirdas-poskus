# Installation Guide

## Requirements:
- Python 3.11 (for usage with FB Prophet, later versions are incompatible).
- Jupyter Notebook

## Create Python Virtual Environment

1. Open PowerShell or Command Prompt.

2. Navigate to your project directory:

   ```
   cd path\to\your\project
3. Create a virtual environment named venv:

    ```
    python -m venv venv
    ```

4. Activate the virtual environment:

    PowerShell:
    
    ```
    .\venv\Scripts\activate.ps1
    ```

    Command Prompt:
    
    ```
   .\venv\Scripts\activate.bat
    ```

5. Install Dependencies

    Run this command to install all packages listed in requirements.txt:

    ```
    pip install -r requirements.txt
    ```