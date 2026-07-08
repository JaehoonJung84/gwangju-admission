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
 *   GET     → staff read (x-staff-key required): default = active list (no deleted, no docFiles);
 *             ?id=<appId> = one full application (with docFiles); ?deleted=1 = the archive.
 *   DELETE  → soft-delete one application by app id (?id=); recoverable. (x-staff-key)
 *   PATCH   → merge fields into one application ({id, patch}); used for restore & review verdict. (x-staff-key)
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
      "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
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

      // ---- Staff read (gated by staff key) ----
      //   ?id=<appId>   → full single application (includes docFiles) for the detail view
      //   ?deleted=1    → the deleted archive
      //   (default)     → active list, excluding deleted rows and the heavy docFiles blob
      if (request.method === "GET") {
        const key = request.headers.get("x-staff-key") || "";
        if (!env.STAFF_KEY || key !== env.STAFF_KEY) {
          return json({ error: "unauthorized" }, 401);
        }
        const url = new URL(request.url);
        const id = url.searchParams.get("id");
        if (id) {
          const r = await neonQuery(
            env.DATABASE_URL,
            "select id, created_at, payload from applications where payload->>'id' = $1 limit 1",
            [id]
          );
          return json(Array.isArray(r.rows) ? r.rows : [], 200);
        }
        const deleted = url.searchParams.get("deleted") === "1";
        const where = deleted
          ? "coalesce(payload->>'deleted','') = 'true'"
          : "coalesce(payload->>'deleted','') <> 'true'";
        const r = await neonQuery(
          env.DATABASE_URL,
          "select id, created_at, (payload - 'docFiles') as payload from applications where " +
            where + " order by created_at desc limit 10000",
          []
        );
        return json(Array.isArray(r.rows) ? r.rows : [], 200);
      }

      // ---- Soft-delete: move to the archive (staff only). Recoverable via PATCH. ----
      if (request.method === "DELETE") {
        const key = request.headers.get("x-staff-key") || "";
        if (!env.STAFF_KEY || key !== env.STAFF_KEY) {
          return json({ error: "unauthorized" }, 401);
        }
        const id = new URL(request.url).searchParams.get("id") || "";
        if (!id) return json({ error: "bad_request: missing id" }, 400);
        const r = await neonQuery(
          env.DATABASE_URL,
          "update applications set payload = payload || jsonb_build_object('deleted', true, 'deletedAt', to_char(now() at time zone 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')) where payload->>'id' = $1",
          [id]
        );
        return json({ ok: true, updated: (r && r.rowCount) || 0 }, 200);
      }

      // ---- Merge fields into an application (staff only). Used for restore + review verdict. ----
      //   body: { "id": "<appId>", "patch": { ...fields to merge... } }
      if (request.method === "PATCH") {
        const key = request.headers.get("x-staff-key") || "";
        if (!env.STAFF_KEY || key !== env.STAFF_KEY) {
          return json({ error: "unauthorized" }, 401);
        }
        let body;
        try { body = await request.json(); } catch (_) { body = null; }
        const id = body && body.id;
        const patch = body && body.patch;
        if (!id || !patch || typeof patch !== "object") {
          return json({ error: "bad_request: expected {id, patch}" }, 400);
        }
        const r = await neonQuery(
          env.DATABASE_URL,
          "update applications set payload = payload || $2::jsonb where payload->>'id' = $1",
          [id, JSON.stringify(patch)]
        );
        return json({ ok: true, updated: (r && r.rowCount) || 0 }, 200);
      }

      return json({ error: "method_not_allowed" }, 405);
    } catch (e) {
      return json({ error: "proxy_exception", detail: String(e && e.message || e) }, e && e.status ? e.status : 502);
    }
  },
};
