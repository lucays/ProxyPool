import re
import sys

from gunicorn.app.wsgiapp import run


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$','',sys.argv[0])
    sys.exit(run())
    # python3 run_gunicorn.py -w 8 -b 0.0.0.0:5000 run_proxy_crawl:app --reload -t 900
