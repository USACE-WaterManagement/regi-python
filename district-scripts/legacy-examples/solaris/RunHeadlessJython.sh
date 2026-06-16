#!/bin/bash

NOT_FOUND="notFound"

PROGRAM_ROOT=$(realpath ..)
JAR_DIR=$PROGRAM_ROOT/lib
SYS=$JAR_DIR/sys
CWMS=$JAR_DIR/cwms
REGI=$JAR_DIR/regi
LIBRARY_PATH=$PROGRAM_ROOT/lib64
JAVA_EXE=$PROGRAM_ROOT/jre64/bin/java
ARGS=("$@")

export LD_LIBRARY_PATH=$LIBRARY_PATH:$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH updated to $LD_LIBRARY_PATH"

ORACLE_URL=$(getProp cwms.dbi.ConnectUsingUrl @${NOT_FOUND} dbi.properties|cut -d@ -f2)
if [ $ORACLE_URL = $NOT_FOUND ]
then
	echo "Unable to locate Oracle URL from Cwms configuration. Will be taken from credentials.properties"
fi

echo "Found Oracle URL: $ORACLE_URL"

# Get the office id from cwms.properties using the CWMS getProp script
OFFICE_ID=$(getProp cwms.OfficeID ${NOT_FOUND} cwms.properties $CWMS_HOME/config/properties)
if [ $OFFICE_ID = $NOT_FOUND ]
then
	echo "Unable to locate OfficeID from Cwms configuration. Will be taken from credentials.properties"
fi

echo "Found Office ID: $OFFICE_ID"

# The password file is expected to be at the following (full) path.
PASSWORD_FILE=$CWMS_HOME/config/properties/dbi.conf
if [ ! -f $PASSWORD_FILE ]
then
	echo "Unable to locate password file in Cwms configuration. Will be taken from credentials.properties"
fi

SCRIPT=""
NAME_FOUND=false

for ((i=0; i < ${#ARGS[@]}; i++))
do
  PARAM_NAME=$(echo "${ARGS[$i]}" | tr '[:lower:]' '[:upper:]')

  if [ "$NAME_FOUND" = true ] ; then
    # Use the script name as the base file name for the log file
    BASENAME="$(basename "${ARGS[$i]}")" # Get only the base file name.
    SCRIPT="${BASENAME%%.*}" # Remove the extension
    break
  elif [ "$PARAM_NAME" = "-F" ] ; then
    NAME_FOUND=true
  fi
done



JAVA_COMMAND="-cp $JAR_DIR/*:$REGI/*:$CWMS/*:$SYS/*:"\
" -Doracle.url=jdbc:oracle:thin:@${ORACLE_URL}"\
" -Doracle.officeId=$OFFICE_ID"\
" -Dhec.passwd=$PASSWORD_FILE"\
" -Djava.library.path=$LIBRARY_PATH"\
" -DPLUGINS=$EXT"\
" -Doracle.metrics.clientid=\"CWMS REGI-Headless-v5.0\""\
" -Djava.util.logging.config.file=../config/properties/logging.properties"\
" -Drowcps.timezone=America/Chicago"\
" usace.rowcps.headless.RegiCLI"\
" -p ..//examples//credentials.properties"\
" ${ARGS[*]}"

LOG_FILE=$CWMS_HOME/cronjobs/headless/logs/$(getStartFN regi-headless-"$SCRIPT")

echo "Running jython $SCRIPT"
echo "Output going to: $LOG_FILE"
echo "Java Command:"
echo "$JAVA_EXE $JAVA_COMMAND"
eval "$JAVA_EXE" $JAVA_COMMAND &> "$LOG_FILE"
STATUS=$?

echo "$SCRIPT process exited with code $STATUS"