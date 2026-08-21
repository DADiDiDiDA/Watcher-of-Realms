Set objShell = CreateObject("WScript.Shell")
objShell.Run "python D:\Application\Automate\Git-Maawork\Tide-Watcher\agent\launch_watcher.py", 0, False

' 等待 15 秒
WScript.Sleep 15000