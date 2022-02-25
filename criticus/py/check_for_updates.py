import toml

from criticus.py import mureq as req
from criticus.py import custom_popups as cp

def check_for_update(current):
    response = req.get('https://raw.githubusercontent.com/d-flood/criticus/master/pyproject.toml')
    data = response.content.decode('utf-8')
    pyproject = toml.loads(data)
    newest = pyproject['tool']['poetry']['version']

    new_ver_message = f"""
There is a newer version of Criticus available!
Your current version is {current}.
The newest available is {newest}.
To upgrade, close Criticus, then copy the relavent 
line below and paste it into a terminal and hit 
Enter (Windows) or Return (MacOS).""".lstrip()

    if newest > current:
        cp.mac_win_cmd(new_ver_message, 'New Version Available', 'pip3 --upgrade criticus', 'pip --upgrade criticus')
    else:
        cp.ok('You already have the newest version of Criticus!', title="You're up to date")
