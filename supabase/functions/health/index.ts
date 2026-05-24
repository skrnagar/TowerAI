import "jsr:@supabase/functions-js/edge-runtime.d.ts";

Deno.serve(() =>
  new Response(JSON.stringify({ service: "towerai", status: "ok" }), {
    headers: { "Content-Type": "application/json" },
  })
);
