# QualisysRobotiqSoftwareTrigger
## Installation
Clone repositroy.<br>
<ins>SSH:</ins><br>
```git clone git@github.com:grashidi/QualisysRobotiqSoftwareTrigger.git```<br><br>
<ins>HTTPS:</ins><br>
```git clone https://github.com/grashidi/QualisysRobotiqSoftwareTrigger.git```<br><br>
Change into the cloned repository.<br>
```cd QualisysRobotiqSoftwareTrigger```<br><br>
Install the required python packages.<br>
```pip3 install -r requirements.txt```<br><br>
Start the synchronization program when QTM is running.<br>
```python3 main.py -d your_directory -f your_filename```<br><br>
Generated data will be stored in <ins>your_directory/your_filename_[counter].txt</ins><br>
Absolute and relative file paths are supported.
