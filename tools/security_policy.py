"""One browser policy for generated HTML, deployment headers and verification."""
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; style-src-attr 'none'; "
    "img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; "
    "base-uri 'none'; form-action 'none'; upgrade-insecure-requests; "
    "require-trusted-types-for 'script'; trusted-types 'none'"
)

# frame-ancestors is effective only in an HTTP header, never in an HTML meta tag.
HEADERS = {
    "Content-Security-Policy": CSP + "; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


def cloudflare_headers() -> str:
    return "/*\n" + "".join(f"  {key}: {value}\n" for key, value in HEADERS.items())
