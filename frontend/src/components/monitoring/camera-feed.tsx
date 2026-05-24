"use client";

import { cn } from "@/lib/utils";
import { Camera, Wifi, WifiOff } from "lucide-react";

interface CameraFeedProps {
  name: string;
  status: "online" | "offline" | "error";
  detections?: number;
  className?: string;
}

export function CameraFeed({ name, status, detections = 0, className }: CameraFeedProps) {
  const isOnline = status === "online";

  return (
    <div className={cn("relative overflow-hidden rounded-lg border border-border bg-black", className)}>
      <div className="scanline absolute inset-0 flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <Camera className="mx-auto h-8 w-8 mb-2 opacity-50" />
          <p className="text-xs">{isOnline ? "Live Feed" : "No Signal"}</p>
        </div>
      </div>

      <div className="absolute top-2 left-2 flex items-center gap-1.5 rounded bg-black/70 px-2 py-1">
        <div className={cn("h-2 w-2 rounded-full", isOnline ? "bg-safe animate-pulse" : "bg-critical")} />
        <span className="text-[10px] font-medium text-white">{name}</span>
      </div>

      <div className="absolute top-2 right-2">
        {isOnline ? (
          <Wifi className="h-3.5 w-3.5 text-safe" />
        ) : (
          <WifiOff className="h-3.5 w-3.5 text-critical" />
        )}
      </div>

      {detections > 0 && (
        <div className="absolute bottom-2 left-2 rounded bg-critical/80 px-2 py-0.5 text-[10px] font-bold text-white">
          {detections} ALERT{detections > 1 ? "S" : ""}
        </div>
      )}
    </div>
  );
}
