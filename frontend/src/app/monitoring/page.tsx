"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { CameraFeed } from "@/components/monitoring/camera-feed";

export default function MonitoringPage() {
  return (
    <DashboardLayout title="Live Monitoring">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <CameraFeed name="CAM-001 — Tower Base" status="offline" className="aspect-video" />
      </div>
    </DashboardLayout>
  );
}
