import { createClient } from "@/utils/supabase/client";

const BUCKET_VIOLATIONS = "violation-screenshots";
const BUCKET_RECORDINGS = "recordings";

/** Signed URL for a violation screenshot (authenticated user). */
export async function getViolationScreenshotUrl(
  path: string,
  expiresIn = 3600
): Promise<string | null> {
  const supabase = createClient();
  const { data, error } = await supabase.storage
    .from(BUCKET_VIOLATIONS)
    .createSignedUrl(path, expiresIn);
  if (error || !data?.signedUrl) return null;
  return data.signedUrl;
}

/** Upload from browser (supervisor dashboard) — requires authenticated session. */
export async function uploadViolationScreenshot(
  file: File,
  path?: string
): Promise<{ path: string } | null> {
  const supabase = createClient();
  const objectPath = path ?? `${crypto.randomUUID()}-${file.name}`;
  const { error } = await supabase.storage.from(BUCKET_VIOLATIONS).upload(objectPath, file, {
    upsert: false,
  });
  if (error) return null;
  return { path: objectPath };
}

export const storageBuckets = {
  violations: BUCKET_VIOLATIONS,
  recordings: BUCKET_RECORDINGS,
} as const;
