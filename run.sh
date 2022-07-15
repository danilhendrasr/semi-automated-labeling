#!/bin/bash

./run_streamlit.sh &  
./run_flask.sh &
./run_dash.sh &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?