
@echo off

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%
set VORTEX=%CD%
set ZOOTOOLS_ROOT=F:\code\python\personal\zootoolspro
set PATH=%PATH%;%ABS_PATH%;%ZOOTOOLS_ROOT%\install\core\python
set VORTEX_ICONS=%ABS_PATH%\icons
set PYTHONPATH=%PYTHONPATH%;%ABS_PATH%;%ZOOTOOLS_ROOT%\install\core\python
set VORTEX_UI_PLUGINS=%ABS_PATH%\vortex\plugins\ui

