for %%i in ("%~dp0.") do SET "VORTEX=%%~fi"
set DEBUG=1
set ZOOTOOLS_ROOT=F:\code\python\personal\zootoolspro
set ZOO_PACKAGE_VERSION_PATH=%VORTEX%\zoo\package_version.config
set PATH=%PATH%;%VORTEX%;%ZOOTOOLS_ROOT%\install\core\python
set VORTEX_ICONS=%VORTEX%\icons
set PYTHONPATH=%PYTHONPATH%;%VORTEX%;%ZOOTOOLS_ROOT%\install\core\python
set VORTEX_UI_PLUGINS=%VORTEX%\vortex\plugins\ui
echo %VORTEX%