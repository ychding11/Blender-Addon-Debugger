
bl_info = {
   'name': 'Blender Addon Debugger',
   'author': 'ychding',
   'version': (0, 0, 1),
   'blender': (2, 80, 0), # supports 2.8+
   "description": "Starts debugging server through ptvsd. Then Visual Studio can attach to it and begins to debug.",
   'location': 'In search (Edit > Operator Search) type "Debug"',
   "warning": "",
   "wiki_url": "https://github.com/ychding11/Blender-Addon-Debugger",
   "tracker_url": "https://github.com/ychding11/Blender-Addon-Debugger/issues",
   'category': 'Development',
}

import bpy
import sys
import os
import subprocess
import re

# finds path to ptvsd if it exists
def check_for_ptvsd():
   #commands to check
   checks = [
      ["where", "python"],
      ["whereis", "python"],
      ["which", "python"],
   ]

   location = None
   for command in checks:
      try:
         location = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
         )
      except Exception:
         continue
      if location is not None:
         location = str(location.communicate()[0], "utf-8")
         #normalize slashes
         location = re.sub("\\\\", "/", location)
         #extract path up to last slash
         match = re.search(".*(/)", location)
         if match is not None:
            match = match.group()
            if os.path.exists(match+"lib/site-packages/ptvsd"):
               match = match+"lib/site-packages"
               return match

   #check in path just in case PYTHONPATH happens to be set
   for path in sys.path:
      path = path.rstrip("/")
      if os.path.exists(path+"/ptvsd"):
         return path
      if os.path.exists(path+"/site-packages/ptvsd"):
         return path+"/site-packages"
      if os.path.exists(path+"/lib/site-packages/ptvsd"):
         return path+"lib/site-packages"
   return "PTVSD not Found"

# Preferences
class DebuggerPreferences(bpy.types.AddonPreferences):
   bl_idname = __name__

   path : bpy.props.StringProperty(
      name="Location of PTVSD",
      subtype="DIR_PATH",
      default=check_for_ptvsd()
   )

   timeout : bpy.props.IntProperty(
      name="Timeout",
      default=20
   )

   port : bpy.props.IntProperty(
      name="Port",
      min=0,
      max=65535,
      default=5678
   )

   def draw(self, context):
      layout = self.layout
      row_path = layout
      row_path.label(text="The addon try to automatically locate ptvsd, if no path is found, or you would like to use another one, set it here.")
      row_path.prop(self, "path")

      row_timeout = layout.split()
      row_timeout.prop(self, "timeout")
      row_timeout.label(text="Timeout in seconds for the attach confirmation listener.")

      row_port = layout.split()
      row_port.prop(self, "port")
      row_port.label(text="Port on which to listen.")

# check if debugger has attached
def check_done(i, modal_limit, prefs):
   if i == 0 or i % 60 == 0:
      print("Waiting... (on port "+str(prefs.port)+")")
   if i > modal_limit:
      print("Attach Confirmation Listener Timed Out")
      return {"CANCELLED"}
   if not ptvsd.is_attached():
      return {"PASS_THROUGH"}
   print('Debugger is Attached')
   return {"FINISHED"}

class DebuggerCheck(bpy.types.Operator):
   bl_idname = "debug.check_for_debugger"
   bl_label = "Debug: Check if debugger is attached"
   bl_description = "Starts modal timer that checks if debugger attached until attached or timeout"

   _timer = None
   count = 0
   modal_limit = 20*60

   # call check_done
   def modal(self, context, event):
      self.count = self.count + 1
      if event.type == "TIMER":
         prefs = bpy.context.preferences.addons[__name__].preferences
         return check_done(self.count, self.modal_limit, prefs)
      return {"PASS_THROUGH"}

   def execute(self, context):
      # set initial variables
      self.count = 0
      prefs = bpy.context.preferences.addons[__name__].preferences
      self.modal_limit = prefs.timeout*60

      wm = context.window_manager
      self._timer = wm.event_timer_add(0.1, window=context.window)
      wm.modal_handler_add(self)
      return {"RUNNING_MODAL"}

   def cancel(self, context):
      print("Debugger Confirmation Cancelled")
      wm = context.window_manager
      wm.event_timer_remove(self._timer)

class DebugServerStart(bpy.types.Operator):
   bl_idname = "debug.connect_debugger_vscode"
   bl_label = "Debug: Start Debug Server for Visual Studio"
   bl_description = "Starts ptvsd server for debugger to attach"

   def execute(self, context):
      prefs = bpy.context.preferences.addons[__name__].preferences
      ptvsd_path = prefs.path.rstrip("/")
      ptvsd_port = prefs.port

      #actually check ptvsd is still available
      if ptvsd_path == "PTVSD not Found":
         self.report({"ERROR"}, "Couldn't detect ptvsd, please specify the path manually in the addon preferences or reload the addon if you installed ptvsd after enabling it.")
         return {"CANCELLED"}

      if not os.path.exists(os.path.abspath(ptvsd_path+"/ptvsd")):
         self.report({"ERROR"}, "Can't find ptvsd at: %r/ptvsd." % ptvsd_path)
         return {"CANCELLED"}

      if not any(ptvsd_path in p for p in sys.path):
         sys.path.append(ptvsd_path)


      global ptvsd 
      import ptvsd

      try:
         # ptvsd.enable_attach() to start the debug server. The default hostname is 0.0.0.0, and the default port is 5678;
         ptvsd.enable_attach(("0.0.0.0", ptvsd_port), redirect_output=True)
      except:
         print("Debug server is already running.")

      # call our confirmation listener
      bpy.ops.debug.check_for_debugger()
      return {"FINISHED"}

classes = (
   DebuggerPreferences,
   DebuggerCheck,
   DebugServerStart,
)
register, unregister = bpy.utils.register_classes_factory(classes)

# __name__ is a special varialbe in python.
# its value depends on how to call this module: from cml or from import.
if __name__ == "__main__":
   register()
