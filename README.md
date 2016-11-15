# cg-deploy-shibboleth

This is the Concourse deployment pipeline for
[shibboleth-boshrelease][eighteenf-shibboleth-boshrelease]

[eighteenf-shibboleth-boshrelease]: https://github.com/18F/shibboleth-boshrelease "18F Shibboleth Boshrelease"

## Using the UAA database with shibboleth for authentication

For this deployment of `shibboleth-boshrelease` we're leveraging the UAA
database to authenticate against the UAA db `user` table and a custom table
named `totp_seed` for joining users with TOTP seed tokens and potentially other
things in the future.

### Schema modifications for UAA database

The schema for the `totp_seed` table in the UAA database is [here in
cg-provision][cg-provision-totpseed]. Three columns are required which are the
`username` and `seed` columns. This will allow Shibboleth to leverage the
[18F/Shibboleth-IdP3-TOTP-Auth][cg-plugin-fork] fork to read and save TOTP seed
tokens to the UAA database.

```sql
CREATE TABLE IF NOT EXISTS totp_seed (
    username varchar(255) PRIMARY KEY,
    seed varchar(36),
    backup_code varchar(36)
)
```

[cg-provision-totpseed]: https://github.com/18F/cg-provision/blob/master/ci/scripts/create-and-update-db.sh#L24-L27 "GitHub 18F/cg-provision file"
[cg-plugin-fork]: https://github.com/18F/Shibboleth-IdP3-TOTP-Auth "GitHub 18F/Shibboleth-IdP3-TOTP-Auth"
