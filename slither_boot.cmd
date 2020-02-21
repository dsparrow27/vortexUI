
@echo off

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%
set VORTEX=%CD%
CALL :NORMALIZEPATH "..\slither"
set SLITHER=%RETVAL%
set PATH=%PATH%;%ABS_PATH%;%SLITHER%;%SLITHER%\thirdparty;
set PYTHONPATH=%PYTHONPATH%;%ABS_PATH%;%SLITHER%;%SLITHER%\thirdparty;
set VORTEX_UI_PLUGINS=%ABS_PATH%\vortex\plugins\ui
set ZOOTOOLS_ROOT=D:\dave\code\python\tools\personal\zootoolspro_install
set pluginBase=D:\dave\code\python\tools\personal\slither\slither\plugins
set nodeLib=%pluginBase%\nodes\generic"
set SLITHER_NODE_LIB=%nodeLib%
set SLITHER_TYPE_LIB=%pluginBase%\datatypes\generic
set DISPATCHER_LIB=%pluginBase%\dispatchers
:NORMALIZEPATH
  SET RETVAL=%~dpfn1
  EXIT /B