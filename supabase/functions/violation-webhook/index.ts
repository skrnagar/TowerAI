// Tower AI — ingest violation payload from AI engine (service role via Authorization header)
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface ViolationPayload {
  camera_id: string;
  site_id: string;
  violation_type: string;
  severity: string;
  confidence: number;
  bounding_boxes?: unknown[];
  frame_timestamp: string;
  screenshot_key?: string;
  tracking_id?: string;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, serviceKey);

  let body: ViolationPayload;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const { data: violation, error: vErr } = await supabase
    .from("violations")
    .insert({
      camera_id: body.camera_id,
      site_id: body.site_id,
      violation_type: body.violation_type,
      severity: body.severity,
      confidence: body.confidence,
      bounding_boxes: body.bounding_boxes ?? [],
      frame_timestamp: body.frame_timestamp,
      screenshot_key: body.screenshot_key,
      tracking_id: body.tracking_id,
    })
    .select("id, violation_type, severity")
    .single();

  if (vErr) {
    return new Response(JSON.stringify({ error: vErr.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const title = `Safety violation: ${body.violation_type}`;
  const { error: aErr } = await supabase.from("alerts").insert({
    violation_id: violation.id,
    camera_id: body.camera_id,
    site_id: body.site_id,
    title,
    message: `${title} (confidence ${body.confidence})`,
    severity: body.severity,
    status: "pending",
  });

  if (aErr) {
    return new Response(JSON.stringify({ error: aErr.message, violation_id: violation.id }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ ok: true, violation_id: violation.id }), {
    status: 201,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
