# Blender-Addon-Debugger
It is a Blender Addon which enables remote debugging from Visual Studio.
[ᴘᴛᴠsᴅ](https://github.com/microsoft/ptvsd) is a python debugger. It supports remote python remote debugging.
It use ptvsd API to start a debugger sever on blender side. After debugger server begins to listen, debugger client (in visual studio) can connect to it. Then
Visual Studio enters debug mode.    As show in following picture.

## Setup
- install the add-on into blender.
  - copying the folder into `D:\Program Files\Blender Foundation\Blender 2.83\2.83\scripts\addons` (It is just an example).
- install ptvsd by command `pip install ptvsd`
- connect to debugger sever in blender. 
  - The detail settings can refer this [page](https://docs.microsoft.com/en-us/visualstudio/python/debugging-python-code-on-remote-linux-machines?view=vs-2019#attach-remotely-from-python-tools)
  
  ## To do
  - use [debugpy](https://github.com/microsoft/debugpy) replace ptvsd.
    - For Visual Studio 2019 version 16.4 and earlier, the ptvsd library was used. The debugpy library replaced ptvsd 4 in Visual Studio 2019 version 16.5.
