mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"hello@dancorley.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
maxUploadSize = 2000\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml