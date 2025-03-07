echo "#!/bin/bash" > startup.sh
echo "gunicorn -w 4 -b 0.0.0.0:8000 server:app" >> startup.sh
chmod +x startup.sh

