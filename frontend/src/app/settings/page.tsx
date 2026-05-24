"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";

export default function SettingsPage() {
  return (
    <DashboardLayout title="Settings">
      <p className="text-muted-foreground">Site, camera, and user configuration.</p>
    </DashboardLayout>
  );
}
