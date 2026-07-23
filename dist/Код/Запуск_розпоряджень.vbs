Set shell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
pythonwPath = "C:\Users\user\AppData\Local\Programs\Python\Python311\pythonw.exe"
command = """" & pythonwPath & """ """ & scriptDir & "\main.py"""
shell.CurrentDirectory = scriptDir
shell.Run command, 0, False
