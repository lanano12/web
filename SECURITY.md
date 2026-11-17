# Reporting a vulnerability

Use [private vulnerability reporting](https://github.com/lanano12/web/security/advisories/new) for issues affecting this website or its published source. Do not include exploit details, credentials or personal information in a public issue.

The [disclosure policy](https://www.nexafusion.io/security/) describes scope and coordination. The [security.txt](https://www.nexafusion.io/.well-known/security.txt) file identifies the current reporting route. This is not a paid bounty programme and there is no guaranteed response time.

# Security boundaries

- The deployed website is static. It has no login, database, upload endpoint or application API.
- Checklist answers and navigation searches stay in memory. Emailing a summary is an explicit user action.
- Update-verification examples use synthetic data and native Web Crypto. They are not production firmware or a certification claim.
- Publishing is restricted to the file list in `tools/package_site.py`. Source tooling and repository history do not belong in the hosted artifact.
- `tools/security_policy.py` defines both the HTML policy and the intended HTTP headers. GitHub Pages does not apply the Cloudflare `_headers` format; passing local checks does not prove live headers are configured.

# Verification

Use Node 24+ and Python 3.11+:

```sh
npm ci --ignore-scripts
python3 tools/build.py
python3 tools/check.py
npm test
python3 tools/package_site.py
npx playwright install chromium
npm run test:browser
```

`python3 tools/check_live.py` checks the public deployment, including HTTP headers. It must fail if required production headers are absent; do not weaken the check to obtain a green result.

Review security.txt before its expiry. Review the actual reporting inbox/notifications, GitHub account authentication, DNS access and deployment permissions separately from source-code checks.
