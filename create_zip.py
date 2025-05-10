import os
import zipfile
from datetime import datetime

def create_zip():
    """Create a zip file of the project."""
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"unimatch_ethiopia_{timestamp}.zip"
    
    # Files to include
    files_to_zip = [
        "README.md",
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "config.py",
        "main.py",
        "web.py",
        "universities.py",
        ".gitignore",
        ".env.example",
        "database/__init__.py",
        "database/database.py",
        "database/models.py",
        "handlers/__init__.py",
        "handlers/keyboards.py",
        "handlers/profile.py",
        "handlers/states.py"
    ]
    
    # Create zip file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file} to zip")
            else:
                print(f"Warning: {file} not found")
    
    print(f"\nZip file created: {zip_filename}")
    print("\nTo use the bot:")
    print("1. Extract the zip file")
    print("2. Create a virtual environment: python -m venv venv")
    print("3. Activate the virtual environment:")
    print("   - Windows: venv\\Scripts\\activate")
    print("   - Unix/MacOS: source venv/bin/activate")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Copy .env.example to .env and fill in your values")
    print("6. Run the bot: python main.py")

if __name__ == "__main__":
    create_zip() 