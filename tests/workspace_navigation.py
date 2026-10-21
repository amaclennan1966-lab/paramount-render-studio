"""Navigate contextual panels before using the original rendering regression controls.

This exercises the real panel navigation API; it does not unhide all panels or
change renderer state, and leaves every existing rendering assertion in place.
"""
from playwright.sync_api import Locator
class WorkspaceLocator:
 def __init__(self,raw): self.raw=raw
 def __getattr__(self,name):
  value=getattr(self.raw,name)
  if isinstance(value,Locator): return WorkspaceLocator(value)
  if not callable(value): return value
  def call(*args,**kwargs):
   if name in {'click','fill','check','uncheck','select_option','set_input_files','focus','evaluate','press','hover'}:
    self.raw.evaluate('el=>window.ParamountWorkspace?.reveal(el)')
   result=value(*args,**kwargs)
   return WorkspaceLocator(result) if isinstance(result,Locator) else result
  return call
class WorkspacePage:
 def __init__(self,raw): self.raw=raw
 def __getattr__(self,name):
  value=getattr(self.raw,name)
  if not callable(value): return value
  def call(*args,**kwargs):
   if name in {'select_option','fill','click','check','uncheck','set_input_files','focus'}:
    self.raw.locator(args[0]).evaluate('el=>window.ParamountWorkspace?.reveal(el)')
   result=value(*args,**kwargs)
   return WorkspaceLocator(result) if isinstance(result,Locator) else result
  return call
