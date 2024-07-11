#!/bin/bash

# Set the installation directory to User's Applications
PROGRAM_FILES="/Applications/PyLabel"

# Create the directory if it doesn't exist
if [ ! -d "$PROGRAM_FILES" ]; then
    mkdir -p "$PROGRAM_FILES"
fi

# Copy application files
cp -R "${0%/*}/PyLabelProgramFiles/" "$PROGRAM_FILES/"

# Grant permissions
chmod -R 755 "$PROGRAM_FILES"

# Check for Python 3.11.9
found_python=false
for py_path in $(which -a python3); do
    py_version=$($py_path --version 2>&1)
    if [[ $py_version == "Python 3.11.9" ]]; then
        found_python=true
        break
    fi
done

if [ "$found_python" = true ]; then
    # Install dependencies
    "$py_path" -m ensurepip
    "$py_path" -m pip install --upgrade pip
    "$py_path" -m pip install -r "$PROGRAM_FILES/requirements.txt"

    # Set up PyLabel command
    echo "#!/bin/bash" > /usr/local/bin/PyLabel
    echo "\"$py_path\" \"$PROGRAM_FILES/PyLabel.py\" \"\$@\"" >> /usr/local/bin/PyLabel
    chmod +x /usr/local/bin/PyLabel
else
    echo "Python 3.11.9 is not installed."
    open "$PROGRAM_FILES/PyInstructions.pdf"
    exit 1
fi

echo "Installation complete. You can now use the command 'PyLabel' from any directory"
