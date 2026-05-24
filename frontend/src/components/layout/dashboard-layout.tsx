"use client";

import { Bell } from "lucide-react";
import { Sidebar } from "./sidebar";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title: string;
  alertCount?: number;
}

export function DashboardLayout({ children, title, alertCount = 0 }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-between border-b border-border bg-card/50 px-6 backdrop-blur">
          <h1 className="text-lg font-semibold">{title}</h1>
          <div className="flex items-center gap-4">
            <button className="relative rounded-md p-2 hover:bg-accent">
              <Bell className="h-5 w-5 text-muted-foreground" />
              {alertCount > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-critical text-[10px] font-bold text-white">
                  {alertCount > 9 ? "9+" : alertCount}
                </span>
              )}
            </button>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                AD
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
