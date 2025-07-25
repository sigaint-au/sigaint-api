# API

API Services that are provided and used by Unix.


## Example Deployment
```
sudo podman run --rm \
    --name sigaint-api \
    -p 5000:5000 \
    -e LDAP_BASE_DN="dc=sigaint,dc=au" \
    -e LDAP_BIND_DN="uid=svc-ldap-bind,cn=users,cn=accounts,dc=sigaint,dc=au" \
    -e LDAP_BIND_PASSWORD="xxxxxxxx" \
    -e SUDO_LDAP_BASE_DN="ou=SUDOers,dc=sigaint,dc=au" \
    -e NETGROUP_LDAP_BASE_DN="cn=ng,cn=compat,dc=sigaint,dc=au" \
    -e LDAP_SERVER_URI="ldaps://ipa-1.syd.sigaint.au" \
    localhost/sigaint-api:latest
```