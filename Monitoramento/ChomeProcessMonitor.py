import psutil #pip install psutil

PROCNAME = "chrome.exe"

for proc in psutil.process_iter():
	#Check whether the process name matches
	if proc.name() == PROCNAME:
		proc.kill()