# `sslmate`

Client for SSLMate's
_[Certificate Transparency Search APIv1](https://sslmate.com/help/reference/ct_search_api_v1)_.

```sh
❯ ./sslmate.py --help
INFO: Showing help with the command 'sslmate.py -- --help'.

NAME
    sslmate.py - Query SSLMate's Certificate Transparency Search APIv1.

SYNOPSIS
    sslmate.py DOMAIN <flags>

DESCRIPTION
    Query SSLMate's Certificate Transparency Search APIv1.

POSITIONAL ARGUMENTS
    DOMAIN
        Type: str
        Domain to search for.

FLAGS
    --include-subdomains=INCLUDE_SUBDOMAINS
        Type: bool
        Default: False
        Also search sub-domains
    -d, --dns-names=DNS_NAMES
        Type: bool
        Default: False
        Show DNS names
    --issuer=ISSUER
        Type: bool
        Default: False
        Show issuer
    -r, --revocation=REVOCATION
        Type: bool
        Default: False
        Show revocation info
    -p, --problem-reporting=PROBLEM_REPORTING
        Type: bool
        Default: False
        Show problem reporting instructions
    -c, --cert-der=CERT_DER
        Type: bool
        Default: False
        Show certificate data
    -a, --after=AFTER
        Type: Optional[int | None]
        Default: None
        issuances discovered after this ID
    -t, --timeout=TIMEOUT
        Type: int
        Default: 10
        seconds to wait for each request

NOTES
    You can also use flags syntax for POSITIONAL ARGUMENTS
```

The output will be [JSON Lines](https://jsonlines.org/) which can be further
filtered by something like [`jq`](https://jqlang.org/):

```sh
❯ jq \
    --compact-output \
    --monochrome-output 'select((.not_after | fromdateiso8601 > now))' domain.jsonl > domain-valid.jsonl
```

…and resolved to an active IP via
[`projectdiscovery/dnsx`](https://github.com/projectdiscovery/dnsx):

```sh
❯ jq -r '.dns_names[]' ./domain-valid.jsonl | dnsx -silent -no-color -a -resp > domain-dnsx.txt
```

Note: the `after` value for a subsequent run can be obtained with:

```sh
❯ tail -n1 domain.jsonl | jq -r '.id'
```
