# QualisysRobotiqSoftwareTrigger

## Setup

Python 3 is required in order to execute the scripts.

Setup steps:

1. Clone the repository `git clone git@github.com:sikupe/QualisysRobotiqSoftwareTrigger.git`
2. Install the requirements `pip3 install -r requirements.txt`

## Running the scripts

Start the synchronization program when QTM is running: `python3 main.py -d your_directory -f your_filename`.

Generated data will be stored in `your_directory/your_filename_[counter].txt`

Absolute and relative file paths are supported.
