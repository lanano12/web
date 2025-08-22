#!/bin/bash

# Define the output log file
LOGFILE="log.txt"

# Empty the log file if it exists or create a new one
> "$LOGFILE"

# Loop over all .h and .cpp files in the current directory
for FILE in *.json *.html *.js *.css; do
    # Check if the file exists (in case there are no .h or .cpp files)
    if [ -e "$FILE" ]; then
        # Output the file name to the log file
        echo "File: $FILE" >> "$LOGFILE"
        
        # Output the contents of the file to the log file
        cat "$FILE" >> "$LOGFILE"
        
        # Add a separator for readability
        echo -e "\n--- End of $FILE ---\n" >> "$LOGFILE"
    fi
done
