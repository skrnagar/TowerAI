"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { StatCard } from "@/components/dashboard/stat-card";
import { ViolationCard } from "@/components/dashboard/violation-card";
import { CameraFeed } from "@/components/monitoring/camera-feed";
import { AlertTriangle, Camera, ShieldAlert, ShieldCheck } from "lucide-react";

export default function DashboardPage() {
  return (
    <DashboardLayout title="Command Center" alertCount={3}>
      <div className="space-y-6">
        {/* KPI Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard title="Active Cameras" value="1 / 1" icon={Camera} variant="safe" />
          <StatCard title="Violations Today" value={0} icon={AlertTriangle} variant="warning" />
          <StatCard title="Critical Alerts" value={0} icon={ShieldAlert} variant="critical" />
          <StatCard title="Compliance Rate" value="100%" icon={ShieldCheck} variant="safe" trend="No violations detected" />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Live Camera Grid */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Live Feeds
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <CameraFeed name="CAM-001 — Tower Base" status="offline" className="aspect-video" />
            </div>
          </div>

          {/* Recent Violations Sidebar */}
          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Recent Violations
            </h2>
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground text-center py-8">
                No violations detected today
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
