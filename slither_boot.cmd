
@echo off

rem // Save value of CD variable (current directory)
set ABS_PATH=%CD%
set VORTEX=%CD%
CALL :NORMALIZEPATH "..\slither"
set SLITHER=%RETVAL%
set PATH=%PATH%;%ABS_PATH%;%SLITHER%;%SLITHER%\thirdparty;
set PYTHONPATH=%PYTHONPATH%;%ABS_PATH%;%SLITHER%;%SLITHER%\thirdparty;
set VORTEX_UI_PLUGINS=%ABS_PATH%\vortex\plugins
CALL :NORMALIZEPATH "..\zootools_pro\bin"
cd %RETVAL%
call %RETVAL%\zoo_cmd.bat
:: ========== FUNCTIONS ==========


:NORMALIZEPATH
  SET RETVAL=%~dpfn1
  EXIT /B