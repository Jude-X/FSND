#!"c:\users\nzubechukwu onyekaba\documents\code\udacity\fyyur\fsnd\projects\01_fyyur\env\scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'alembic==1.5.4','console_scripts','alembic'
__requires__ = 'alembic==1.5.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('alembic==1.5.4', 'console_scripts', 'alembic')()
    )
