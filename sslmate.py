#!/usr/bin/env python3

import json
import logging
import os
import sys
import time

import fire
import requests

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stderr,
    force=True,
)
logger = logging.getLogger("sslmate")


def _print_jsonl(records: list[dict]) -> None:
    """
    Write records to stdout as JSON-lines.

    :param records: CT records to be displayed
    """
    output = "\n".join(json.dumps(record) for record in records) + "\n"

    sys.stdout.write(output)
    sys.stdout.flush()


def issuance(
    domain: str,
    include_subdomains: bool = False,
    dns_names: bool = False,
    issuer: bool = False,
    revocation: bool = False,
    problem_reporting: bool = False,
    cert_der: bool = False,
    after: int | None = None,
    timeout: int = 10,
):
    """
    Query SSLMate's Certificate Transparency Search APIv1.

    :param domain: Domain to search for.
    :param include_subdomains: Also search sub-domains
    :param dns_names: Show DNS names
    :param issuer: Show issuer
    :param revocation: Show revocation info
    :param problem_reporting: Show problem reporting instructions
    :param cert_der: Show certificate data
    :param after: issuances discovered after this ID
    :param timeout: seconds to wait for each request
    """

    if not (api_key := os.environ.get("SSLMATE_API_KEY")):
        print("Set the SSLMATE_API_KEY environment variable.")
        sys.exit(1)

    base_url = "https://api.certspotter.com/v1/issuances"
    params: dict[str, str | list[str]] = {
        "domain": domain,
    }

    if include_subdomains:
        params["include_subdomains"] = "true"

    expand_fields = []
    if cert_der:
        expand_fields.append("cert_der")
    if dns_names:
        expand_fields.append("dns_names")
    if issuer:
        expand_fields.append("issuer")
    if revocation:
        expand_fields.append("revocation")
    if problem_reporting:
        expand_fields.append("problem_reporting")

    if expand_fields:
        params["expand"] = expand_fields

    while True:
        if after:
            params["after"] = str(after)

        try:
            response = requests.get(
                base_url,
                params=params,
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
                timeout=timeout,
            )
            logger.info(f"Received {len(response.json())} records for {domain}.")

            _print_jsonl(response.json())

            if retry_after := int(response.headers.get("Retry-After", "0")):
                logging.info(
                    f"Empty results found; retrying after {retry_after} seconds…"
                )
                time.sleep(retry_after)
                continue

            after = response.json()[-1]["id"]

            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error: {e}.")
            sys.exit(1)


if __name__ == "__main__":
    import fire.core

    # TODO: avoid Fire's pager.
    fire.core.Display = lambda lines, out: out.write("\n".join(lines) + "\n")
    fire.Fire(issuance)
