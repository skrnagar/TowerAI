"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";

export default function ViolationsPage() {
  return (
    <DashboardLayout title="Violations">
      <p className="text-muted-foreground">Violation history and incident logs will appear here.</p>
    </DashboardLayout>
  );
}
