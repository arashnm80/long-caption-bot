# this script restarts long caption bot
# it closes the processes from before and starts it again

# Define the script name
SCRIPT_NAME="long_caption_bot.py"

# Find and kill the running process
echo "Finding and killing the alfred process..."
PID=$(pgrep -f "$SCRIPT_NAME")

if [ -n "$PID" ]; then
    echo "Killing process with PID $PID..."
    kill -9 "$PID"
else
    echo "No running process found."
fi

# get address of current script file (which is repository directory)
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Navigate to the script's directory
cd "$SCRIPT_DIR"

# start python file of alfred with logging output to alfred.log
nohup python3 "$SCRIPT_NAME" > /dev/null 2>&1 &