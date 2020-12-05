for %%i in ("%~dp0.") do SET "VORTEX=%%~fi"
set DEBUG=0
set ZOOTOOLS_ROOT=F:\code\python\personal\zootoolspro
set ZOO_PACKAGE_VERSION_PATH=%VORTEX%\zoo\package_version.config
set PATH=%PATH%;%VORTEX%;%ZOOTOOLS_ROOT%\install\core\python
set PYTHONPATH=%PYTHONPATH%;%VORTEX%;%ZOOTOOLS_ROOT%\install\core\python
echo %VORTEX%