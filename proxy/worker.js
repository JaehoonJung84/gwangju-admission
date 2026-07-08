/**
 * Gwangju University Admissions — Neon proxy (Cloudflare Worker)
 *
 * Why this exists:
 *   The Neon Data API requires a JWT bearer token on EVERY request (even anonymous
 *   access needs a short-lived JWT), so the browser can never POST "token-less".
 *   Instead of chasing expiring JWTs, this proxy connects straight to Neon Postgres
 *   over Neon's SQL-over-HTTP endpoint using a connection string kept server-side.
 *   The connection string never touches the public page; reads are staff-key gated.
 *
 * Endpoints (single URL, method-based):
 *   POST    → INSERT a student submission into `applications` (open; the public form).
 *   GET     → SELECT all applications, ONLY if header `x-staff-key` === STAFF_KEY.
 *   OPTIONS → CORS preflight.
 *
 * Request/response contract (matches Gwangju_Admission_System.html):
 *   POST body: {"payload": { ...application... }}          → 201 {"ok":true}
 *   GET  resp: [ {"id":.., "created_at":.., "payload":{..}}, ... ]
 *
 * Secrets / vars (set in the Cloudflare dashboard → Settings → Variables):
 *   DATABASE_URL  (secret)  Neon connection string, e.g.
 *                           postgresql://USER:PASS@ep-xxx-pooler.<region>.aws.neon.tech/neondb?sslmode=require
 *   STAFF_KEY     (secret)  shared secret staff type once to read the dashboard
 *   ALLOW_ORIGIN  (var)     e.g. https://jaehoonjung84.github.io  (or * for any origin)
 *
 * Table (create once in Neon SQL Editor if missing):
 *   create table if not exists applications (
 *     id         bigint generated always as identity primary key,
 *     payload    jsonb not null,
 *     created_at timestamptz not null default now()
 *   );
 */

/* Run one SQL statement against Neon over HTTP (no driver/library needed).
   Protocol mirrors @neondatabase/serverless httpQuery: POST https://{host}/sql
   with the connection string in a header and {query, params} as the body.
   Omitting Neon-Raw-Text-Output / Neon-Array-Mode makes the endpoint return
   typed JSON row objects (jsonb → object, timestamptz → ISO string). */
async function neonQuery(connectionString, query, params) {
  const host = new URL(connectionString).host; // e.g. ep-xxx-pooler.<region>.aws.neon.tech
  const res = await fetch(`https://${host}/sql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Neon-Connection-String": connectionString,
    },
    body: JSON.stringify({ query, params: params || [] }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = (data && (data.message || data.error)) || ("neon_http_" + res.status);
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return data; // { command, rowCount, rows, fields, ... }
}

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

    if (!env.DATABASE_URL) {
      return json({ error: "proxy_misconfigured: set DATABASE_URL secret" }, 500);
    }

    try {
      // ---- Student submission (open) ----
      if (request.method === "POST") {
        let body;
        try { body = await request.json(); } catch (_) { body = null; }
        const payload = body && body.payload !== undefined ? body.payload : body;
        if (!payload || typeof payload !== "object") {
          return json({ error: "bad_request: expected {\"payload\": {...}}" }, 400);
        }
        await neonQuery(
          env.DATABASE_URL,
          "insert into applications (payload) values ($1::jsonb)",
          [JSON.stringify(payload)]
        );
        return json({ ok: true }, 201);
      }

      // ---- Staff dashboard read (gated by staff key) ----
      if (request.method === "GET") {
        const key = request.headers.get("x-staff-key") || "";
        if (!env.STAFF_KEY || key !== env.STAFF_KEY) {
          return json({ error: "unauthorized" }, 401);
        }
        const data = await neonQuery(
          env.DATABASE_URL,
          "select id, created_at, payload from applications order by created_at desc limit 10000",
          []
        );
        return json(Array.isArray(data.rows) ? data.rows : [], 200);
      }

      return json({ error: "method_not_allowed" }, 405);
    } catch (e) {
      return json({ error: "proxy_exception", detail: String(e && e.message || e) }, e && e.status ? e.status : 502);
    }
  },
};
