# cg-deploy-shibboleth

This is the Concourse deployment pipeline for
[shibboleth-boshrelease][eighteenf-shibboleth-boshrelease]

[eighteenf-shibboleth-boshrelease]: https://github.com/18F/shibboleth-boshrelease "18F Shibboleth Boshrelease"

## Using the UAA database with shibboleth for authentication

In this boshrelease, we're leveraging the UAA database to `etc...`

### Schema modifications for UAA database

> See cg-provision, and talk a bit about the schema

### Possible issues in the future

> Talk a bit about what would happen if the UAA db destroys our table and how
> the spec covers the contingency plan.
