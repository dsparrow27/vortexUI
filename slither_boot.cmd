
@echo off

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%

CALL :NORMALIZEPATH "..\slither"
set SLITHER=%RETVAL%
set PATH=%PATH%;%ABS_PATH%;%SLITHER%;
set PYTHONPATH=%PYTHONPATH%;%ABS_PATH%;%SLITHER%;
set VORTEX_UI_PLUGINS=%ABS_PATH%\vortex\plugins
echo %VORTEX_UI_PLUGINS%
echo %PYTHONPATH%
CALL :NORMALIZEPATH "..\zootools_pro\bin"
cd %RETVAL%
call ./zoo_cmd.bat

:: ========== FUNCTIONS ==========
EXIT /B

:NORMALIZEPATH
  SET RETVAL=%~dpfn1
  EXIT /B