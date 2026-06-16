:: The headless scripts can also be executed from a bat file as demonstrated below
@echo off
setlocal enabledelayedexpansion

set next_is_target=0
for %%a in (%*) do (
  if !next_is_target! == 1 (
    set f_value=%%a
    for %%b in ("!f_value!") do set "SCRIPT=%%~nb"
    set next_is_target=0
  ) else (
    if "%%a"=="-f" (
      set next_is_target=1
    )
  )
)

set PROGRAM_ROOT=..
set JAR_DIR=%PROGRAM_ROOT%\lib
set SYS=%JAR_DIR%\sys
set CWMS=%JAR_DIR%\cwms
set REGI=%JAR_DIR%\regi
set LIBRARY_PATH=%PROGRAM_ROOT%\lib64
set JAVA_EXE=%PROGRAM_ROOT%\jre64\bin\java.exe
set ARGS=%*
for /F "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set DATE_TIME=%%I
set DATE_TIME=%DATE_TIME:~0,4%.%DATE_TIME:~4,2%.%DATE_TIME:~6,2%.%DATE_TIME:~8,2%.%DATE_TIME:~10,2%
set LOG_FILE=%CWMS_HOME%\cronjobs\headless\logs\regi-headless-%SCRIPT%.start.%DATE_TIME%.utc

set JAVA_COMMAND=-cp %JAR_DIR%\*;%REGI%\*;%CWMS%\*;%SYS%\*; ^
-Dhec.passwd=%CWMS_HOME%\config\properties\dbi.conf ^
-Djava.library.path=%LIBRARY_PATH% ^
-DPLUGINS=%JAR_DIR%\ext ^
-Doracle.metrics.clientid="CWMS REGI-Headless-v5.0" ^
-Djava.util.logging.config.file=%PROGRAM_ROOT%\config\properties\logging.properties ^
-Drowcps.timezone=America\Chicago ^
usace.rowcps.headless.RegiCLI ^
-p %PROGRAM_ROOT%\examples\credentials.properties ^
%ARGS%

echo Running CWMS-REGI Headless script %SCRIPT%
echo Output going to: %LOG_FILE%
echo Java command:
echo %JAVA_EXE% %JAVA_COMMAND%
%JAVA_EXE% %JAVA_COMMAND% > %LOG_FILE% 2>&1
echo Status: %ERRORLEVEL% >> %LOG_FILE%
endlocal