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

There are two tables which are created for Shibboleth to work properly for TOTP
authentication and multi-zone Shibboleth HA. These tables modify the `uaadb`
directly.

#### TOTP seed table for multi-factor authentication

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

#### Storage records table for multi-zone Shibboleth HA

The schema for the `storagerecords` table in the UAA database is [here in
cg-provision][cg-provision-storagerecords]. This table is used to maintain
session state between Shibboleth instances across availability zones.

```sql
CREATE TABLE storagerecords (
  context varchar(255) NOT NULL,
  id varchar(255) NOT NULL,
  expires bigint DEFAULT NULL,
  value text NOT NULL,
  version bigint NOT NULL,
  PRIMARY KEY (context, id)
)
```

For more information on this, take a look
[here](https://wiki.shibboleth.net/confluence/display/IDP30/StorageConfiguration#StorageConfiguration-JPAStorageService).

[cg-provision-totpseed]: https://github.com/18F/cg-provision/blob/master/ci/scripts/create-and-update-db.sh#L27 "GitHub 18F/cg-provision file"
[cg-provision-storagerecords]: https://github.com/18F/cg-provision/blob/master/ci/scripts/create-and-update-db.sh#L28 "GitHub 18F/cg-provision file"
[cg-plugin-fork]: https://github.com/18F/Shibboleth-IdP3-TOTP-Auth "GitHub 18F/Shibboleth-IdP3-TOTP-Auth"

## Rotating signing and encryption certificates for Shibboleth

Use bosh interpolate to generate these certs, e.g. for production:

```
 bosh interpolate --vars-file=bosh/varsfiles/production.yml --vars-store=prod-creds.yml bosh/manifest.yml
 ```

Be sure to add the bosh ca (which is also the default_ca) as either a vars file argument or just copy and paste into the file `bosh/varsfiles/production.yml`.  The new creds will be stored in `prod-creds.yml`.  Remove the `BEGIN` AND `END` lines from the certs; add these certs to the vars store for shibboleth and deploy.  To finish the rotation, also find and replace these certs in the idp metadata xml for the respective CloudFoundry deployment and deploy CF.

