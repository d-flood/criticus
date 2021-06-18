import http.server as server
import threading
import shutil
import socketserver
from pathlib import Path
import os
import platform
import sys


def start_tei_server(tei_repo_dir, main_dir, httpd, PORT):
    tei_repo_dir = Path(tei_repo_dir).as_posix()
    main_dir = Path(main_dir).as_posix()
    try:
        shutil.copy(f'{main_dir}/tei_transcription.xsl', tei_repo_dir)
    except:
        pass
    print('changing to tei dir')
    os.chdir(tei_repo_dir)
    print(f'Server started at localhost: {PORT}')
    sys.stdout = sys.stderr = open(os.devnull, "w")
    httpd.serve_forever(1)


def launch_tei_viewer(tei_repo_dir, main_dir) -> socketserver.TCPServer:
    PORT = 8011
    handler = server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('', PORT), handler)
    t = threading.Thread(target=start_tei_server, args=[tei_repo_dir, main_dir, httpd, PORT], daemon=True)
    t.start()
    try:
        if platform.system() == 'Windows':
            from subprocess import Popen
            Popen('start firefox http:localhost:8011', shell=True)
        else:
            import webbrowser
            webbrowser.get('firefox').open('http:localhost:8011')
    except:
        print('cold not open browser')
    return httpd
