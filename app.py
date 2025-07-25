import os
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

## Environment Variables
LDAP_BIND_DN = os.environ['LDAP_BIND_DN']
LDAP_BIND_PASSWORD = os.environ['LDAP_BIND_PASSWORD']
LDAP_SERVER_URI = os.environ['LDAP_SERVER_URI']
SUDO_LDAP_BASE_DN = os.environ['SUDO_LDAP_BASE_DN']
NETGROUP_LDAP_BASE_DN = os.environ['NETGROUP_LDAP_BASE_DN']

# Example: cn=ng,cn=compat,dc=sigaint,dc=au
# Example: ou=SUDOers, dc=sigaint,dc=au
# ldaps://ipa-1.syd.sigaint.au
# Example: Hello
# Example: uid=svc-ldap-bind,cn=users,cn=accounts,dc=sigaint,dc=au

def _parse_netgroup_ldif(ldif):
    ldif = ldif.decode('utf-8')
    netgroups = {}

    def _parse_block(block):
        netgroup = None
        triples = []
        for line in block.splitlines():
            if line.startswith('cn:'):
                netgroup = line.split(':')[1].strip()
            if line.startswith('nisNetgroupTriple:'):
                triples.append(line.split(':')[1].strip())
        if not netgroup:
            return
        netgroups[netgroup] = triples

    for block in ldif.split("\n\n"):
        _parse_block(block)
    return netgroups

def _ldap_search(ldap_filter='(objectClass=*)', base=None):
    """
    Return a string containing ldap search result.
    :param ldap_filter:
    :param base:
    :return:
    """
    search = subprocess.Popen(
        [ 'ldapsearch',
          '-x', '-LLL',
          '-H', LDAP_SERVER_URI,
          '-D', LDAP_BIND_DN,
          '-w', LDAP_BIND_PASSWORD,
          '-b', base,
          ldap_filter],
        stdout=subprocess.PIPE
    )
    return search.communicate()[0]

def get_sudoers_from_ldap():
    """
    Return a sudoers file from ldap search.
    :return: String containing sudoers file.
    """
    # Return the ldiff output of all sudoRules
    # sudoCommands and the rest from an LDAP search.
    #
    ldapsearch = _ldap_search('(objectClass=*)', SUDO_LDAP_BASE_DN)

    # Convert the ldif to sudoers format by passing the ldiff from
    # the ldap search to the cvtsudo program.
    #
    cvtsudoers = subprocess.Popen(
        [ 'cvtsudoers',
               '-i', 'ldif',
               '-f', 'sudoers',
               '-o', '-'
          ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    cvtsudoers_output = cvtsudoers.communicate(input=ldapsearch)[0]
    return cvtsudoers_output.decode('utf-8')

def get_netgroups_from_ldap():
    ldif = _ldap_search('(objectClass=nisNetgroup)', NETGROUP_LDAP_BASE_DN)
    netgroups = _parse_netgroup_ldif(ldif)
    return netgroups

@app.route('/api/v1/sudoers')
def api_v1_sudoers():  # put application's code here
    return render_template('sudoers.j2', specification=get_sudoers_from_ldap())

@app.route('/api/v1/netgroups')
def api_v1_netgroups():  # put application's code here
    response = ""
    netgroups = get_netgroups_from_ldap()
    for netgroup, triple in netgroups.items():
        response += f"# nisNetgroup: {netgroup}\n"
        response += f"{netgroup} {" ".join(triple)}\n\n"
    return render_template('netgroups.j2', netgroups=response)

if __name__ == '__main__':
    app.run()
