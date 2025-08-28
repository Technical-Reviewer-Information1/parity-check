# Suggested Commands

## Running the Application
```bash
streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
```
The app will be available at http://localhost:8501

## Development Commands
```bash
# Install dependencies
pip3 install --user -r requirements.txt

# Install Streamlit specifically
pip3 install --user streamlit
```

## System Commands
Since this is running on Linux (Bullseye), standard Linux commands are available:
- `ls` - list files
- `cd` - change directory
- `grep` - search text
- `find` - find files
- `git` - version control

## Dev Container
The project uses a dev container that automatically:
- Installs all requirements
- Starts the Streamlit server on port 8501
- Opens the application in preview mode