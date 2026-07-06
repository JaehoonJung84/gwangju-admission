/**
 * Gwangju University Admissions — Neon Data API proxy (Cloudflare Worker)
 *
 * Why this exists:
 *   The Neon Data API requires a JWT bearer token on EVERY request. Putting that
 *   token in the public GitHub Pages HTML would expose the whole applicants table
 *   (passport numbers, etc.) to anyone. This proxy keeps the token server-side and
 *   protects reads with a staff-only key.
 *
 * Endpoints (single URL, method-based):
 *   POST  → forward student submission to Neon (open; the public application form).
 *   GET   → return all applications, but ONLY if header `x-staff-key` matches STAFF_KEY.
 *   OPTIONS → CORS preflight.
 *
 * Secrets / vars (set in Cloudflare, see README):
 *   NEON_URL      (var)    e.g. https://ep-...neon.tech/neondb/rest/v1/applications
 *   NEON_TOKEN    (secret) the Neon Data API JWT bearer token
 *   STAFF_KEY     (secret) shared secret staff type once to read the dashboard
 *   ALLOW_ORIGIN  (var)    e.g. https://jaehoonjung84.github.io  (or * for any)
 */

export default {
  async fetch(request, env) {
    const origin = env.ALLOW_ORIGIN || "*";
    const cors = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, x-staff-key",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    };
    const json = (obj, status) =>
      new Response(JSON.stringify(obj), {
        status: status || 200,
        headers: { ...cors, "Content-Type": "application/json; charset=utf-8" },
      });

    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const neonUrl = env.NEON_URL;
    if (!neonUrl || !env.NEON_TOKEN) {
      return json({ error: "proxy_misconfigured: set NEON_URL and NEON_TOKEN" }, 500);
    }
    const auth = { Authorization: "Bearer " + env.NEON_TOKEN };

    try {
      // ---- Student submission (open) ----
      if (request.method === "POST") {
        const body = await request.text();
        const r = await fetch(neonUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json", Prefer: "return=minimal", ...auth },
          body,
        });
        if (!r.ok) return json({ error: "neon_post_failed", status: r.status, detail: await r.text() }, r.status);
        return json({ ok: true }, 201);
      }

      // ---- Staff dashboard read (gated by staff key) ----
      if (request.method === "GET") {
        const key = request.headers.get("x-staff-key") || "";
        if (!env.STAFF_KEY || key !== env.STAFF_KEY) {
          return json({ error: "unauthorized" }, 401);
        }
        // pull newest first if the table has a created_at column; harmless if it doesn't
        const url = neonUrl + (neonUrl.includes("?") ? "&" : "?") + "limit=10000";
        const r = await fetch(url, { headers: { Accept: "application/json", ...auth } });
        const text = await r.text();
        return new Response(text, {
          status: r.status,
          headers: { ...cors, "Content-Type": "application/json; charset=utf-8" },
        });
      }

      return json({ error: "method_not_allowed" }, 405);
    } catch (e) {
      return json({ error: "proxy_exception", detail: String(e) }, 502);
    }
  },
};
