"use client";

import { cn, formatTimestamp, getSeverityBg, getSeverityColor } from "@/lib/utils";

interface ViolationCardProps {
  id: string;
  violationType: string;
  severity: string;
  confidence: number;
  cameraName?: string;
  trackingId?: string;
  timestamp: string;
  onAcknowledge?: () => void;
}

const VIOLATION_LABELS: Record<string, string> = {
  helmet_off: "No Helmet Detected",
  harness_off: "No Harness Detected",
  restricted_zone: "Restricted Zone Entry",
  unsafe_climbing: "Unsafe Climbing Posture",
  lifeline_off: "Lifeline Not Attached",
};

export function ViolationCard({
  violationType,
  severity,
  confidence,
  cameraName,
  trackingId,
  timestamp,
}: ViolationCardProps) {
  return (
    <div className={cn("rounded-lg border p-4", getSeverityBg(severity))}>
      <div className="flex items-start justify-between">
        <div>
          <p className={cn("text-sm font-semibold", getSeverityColor(severity))}>
            {VIOLATION_LABELS[violationType] || violationType}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {cameraName && `${cameraName} · `}
            {trackingId && `Worker ${trackingId} · `}
            {formatTimestamp(timestamp)}
          </p>
        </div>
        <span className="text-xs font-mono text-muted-foreground">
          {(confidence * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
