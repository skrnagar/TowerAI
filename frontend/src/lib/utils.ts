import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(new Date(date));
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case "critical":
      return "text-critical";
    case "medium":
      return "text-warning";
    default:
      return "text-muted-foreground";
  }
}

export function getSeverityBg(severity: string): string {
  switch (severity) {
    case "critical":
      return "bg-critical/10 border-critical/30";
    case "medium":
      return "bg-warning/10 border-warning/30";
    default:
      return "bg-muted/10 border-muted/30";
  }
}
