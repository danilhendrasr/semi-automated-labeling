streamlit_port=$(python -c "exec(\"import config\nprint(config.port['streamlit'])\")")
max_upload_size=$(python -c "exec(\"import config\nprint(config.max_upload_size)\")")
cd ./apps/streamlit/
streamlit run main.py --server.port $streamlit_port --server.maxUploadSize $max_upload_size