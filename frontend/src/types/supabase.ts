export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      alerts: {
        Row: {
          assigned_to: string | null
          camera_id: string
          created_at: string | null
          id: string
          message: string
          resolution_note: string | null
          resolved_at: string | null
          resolved_by: string | null
          severity: Database["public"]["Enums"]["violation_severity"]
          site_id: string
          status: Database["public"]["Enums"]["alert_status"] | null
          title: string
          updated_at: string | null
          violation_id: string
        }
        Insert: {
          assigned_to?: string | null
          camera_id: string
          created_at?: string | null
          id?: string
          message: string
          resolution_note?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          severity: Database["public"]["Enums"]["violation_severity"]
          site_id: string
          status?: Database["public"]["Enums"]["alert_status"] | null
          title: string
          updated_at?: string | null
          violation_id: string
        }
        Update: {
          assigned_to?: string | null
          camera_id?: string
          created_at?: string | null
          id?: string
          message?: string
          resolution_note?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          severity?: Database["public"]["Enums"]["violation_severity"]
          site_id?: string
          status?: Database["public"]["Enums"]["alert_status"] | null
          title?: string
          updated_at?: string | null
          violation_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "alerts_assigned_to_fkey"
            columns: ["assigned_to"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "alerts_camera_id_fkey"
            columns: ["camera_id"]
            isOneToOne: false
            referencedRelation: "cameras"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "alerts_resolved_by_fkey"
            columns: ["resolved_by"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "alerts_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "sites"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "alerts_violation_id_fkey"
            columns: ["violation_id"]
            isOneToOne: false
            referencedRelation: "violations"
            referencedColumns: ["id"]
          },
        ]
      }
      audit_logs: {
        Row: {
          action: string
          created_at: string | null
          details: Json | null
          id: string
          ip_address: unknown
          resource_id: string | null
          resource_type: string | null
          user_agent: string | null
          user_id: string | null
        }
        Insert: {
          action: string
          created_at?: string | null
          details?: Json | null
          id?: string
          ip_address?: unknown
          resource_id?: string | null
          resource_type?: string | null
          user_agent?: string | null
          user_id?: string | null
        }
        Update: {
          action?: string
          created_at?: string | null
          details?: Json | null
          id?: string
          ip_address?: unknown
          resource_id?: string | null
          resource_type?: string | null
          user_agent?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "audit_logs_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      cameras: {
        Row: {
          code: string
          created_at: string | null
          fps: number | null
          id: string
          is_active: boolean | null
          last_seen_at: string | null
          latitude: number | null
          location_label: string | null
          longitude: number | null
          name: string
          resolution: string | null
          restricted_zones: Json | null
          rtsp_url: string
          site_id: string
          status: Database["public"]["Enums"]["camera_status"] | null
          updated_at: string | null
        }
        Insert: {
          code: string
          created_at?: string | null
          fps?: number | null
          id?: string
          is_active?: boolean | null
          last_seen_at?: string | null
          latitude?: number | null
          location_label?: string | null
          longitude?: number | null
          name: string
          resolution?: string | null
          restricted_zones?: Json | null
          rtsp_url: string
          site_id: string
          status?: Database["public"]["Enums"]["camera_status"] | null
          updated_at?: string | null
        }
        Update: {
          code?: string
          created_at?: string | null
          fps?: number | null
          id?: string
          is_active?: boolean | null
          last_seen_at?: string | null
          latitude?: number | null
          location_label?: string | null
          longitude?: number | null
          name?: string
          resolution?: string | null
          restricted_zones?: Json | null
          rtsp_url?: string
          site_id?: string
          status?: Database["public"]["Enums"]["camera_status"] | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cameras_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "sites"
            referencedColumns: ["id"]
          },
        ]
      }
      recordings: {
        Row: {
          camera_id: string
          created_at: string | null
          duration_seconds: number | null
          end_time: string | null
          file_key: string | null
          file_size_bytes: number | null
          file_url: string | null
          id: string
          metadata: Json | null
          site_id: string
          start_time: string
          status: Database["public"]["Enums"]["recording_status"] | null
        }
        Insert: {
          camera_id: string
          created_at?: string | null
          duration_seconds?: number | null
          end_time?: string | null
          file_key?: string | null
          file_size_bytes?: number | null
          file_url?: string | null
          id?: string
          metadata?: Json | null
          site_id: string
          start_time: string
          status?: Database["public"]["Enums"]["recording_status"] | null
        }
        Update: {
          camera_id?: string
          created_at?: string | null
          duration_seconds?: number | null
          end_time?: string | null
          file_key?: string | null
          file_size_bytes?: number | null
          file_url?: string | null
          id?: string
          metadata?: Json | null
          site_id?: string
          start_time?: string
          status?: Database["public"]["Enums"]["recording_status"] | null
        }
        Relationships: [
          {
            foreignKeyName: "recordings_camera_id_fkey"
            columns: ["camera_id"]
            isOneToOne: false
            referencedRelation: "cameras"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "recordings_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "sites"
            referencedColumns: ["id"]
          },
        ]
      }
      sites: {
        Row: {
          address: string | null
          code: string
          created_at: string | null
          description: string | null
          id: string
          is_active: boolean | null
          latitude: number | null
          longitude: number | null
          name: string
          timezone: string | null
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          code: string
          created_at?: string | null
          description?: string | null
          id?: string
          is_active?: boolean | null
          latitude?: number | null
          longitude?: number | null
          name: string
          timezone?: string | null
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          code?: string
          created_at?: string | null
          description?: string | null
          id?: string
          is_active?: boolean | null
          latitude?: number | null
          longitude?: number | null
          name?: string
          timezone?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      users: {
        Row: {
          created_at: string | null
          email: string
          full_name: string
          id: string
          is_active: boolean | null
          last_login_at: string | null
          password_hash: string
          role: Database["public"]["Enums"]["user_role"]
          site_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email: string
          full_name: string
          id?: string
          is_active?: boolean | null
          last_login_at?: string | null
          password_hash: string
          role?: Database["public"]["Enums"]["user_role"]
          site_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string
          full_name?: string
          id?: string
          is_active?: boolean | null
          last_login_at?: string | null
          password_hash?: string
          role?: Database["public"]["Enums"]["user_role"]
          site_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "users_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "sites"
            referencedColumns: ["id"]
          },
        ]
      }
      violations: {
        Row: {
          acknowledged_at: string | null
          acknowledged_by: string | null
          bounding_boxes: Json
          camera_id: string
          confidence: number
          created_at: string | null
          frame_timestamp: string
          id: string
          is_acknowledged: boolean | null
          metadata: Json | null
          screenshot_key: string | null
          screenshot_url: string | null
          severity: Database["public"]["Enums"]["violation_severity"]
          site_id: string
          tracking_id: string | null
          violation_type: Database["public"]["Enums"]["violation_type"]
        }
        Insert: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          bounding_boxes?: Json
          camera_id: string
          confidence: number
          created_at?: string | null
          frame_timestamp: string
          id?: string
          is_acknowledged?: boolean | null
          metadata?: Json | null
          screenshot_key?: string | null
          screenshot_url?: string | null
          severity: Database["public"]["Enums"]["violation_severity"]
          site_id: string
          tracking_id?: string | null
          violation_type: Database["public"]["Enums"]["violation_type"]
        }
        Update: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          bounding_boxes?: Json
          camera_id?: string
          confidence?: number
          created_at?: string | null
          frame_timestamp?: string
          id?: string
          is_acknowledged?: boolean | null
          metadata?: Json | null
          screenshot_key?: string | null
          screenshot_url?: string | null
          severity?: Database["public"]["Enums"]["violation_severity"]
          site_id?: string
          tracking_id?: string | null
          violation_type?: Database["public"]["Enums"]["violation_type"]
        }
        Relationships: [
          {
            foreignKeyName: "violations_acknowledged_by_fkey"
            columns: ["acknowledged_by"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "violations_camera_id_fkey"
            columns: ["camera_id"]
            isOneToOne: false
            referencedRelation: "cameras"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "violations_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "sites"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      alert_status: "pending" | "acknowledged" | "resolved" | "dismissed"
      camera_status: "online" | "offline" | "error" | "maintenance"
      recording_status: "recording" | "completed" | "failed" | "archived"
      user_role: "admin" | "supervisor" | "operator" | "viewer"
      violation_severity: "critical" | "high" | "medium" | "low"
      violation_type:
        | "helmet_off"
        | "harness_off"
        | "restricted_zone"
        | "unsafe_climbing"
        | "lifeline_off"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {
      alert_status: ["pending", "acknowledged", "resolved", "dismissed"],
      camera_status: ["online", "offline", "error", "maintenance"],
      recording_status: ["recording", "completed", "failed", "archived"],
      user_role: ["admin", "supervisor", "operator", "viewer"],
      violation_severity: ["critical", "high", "medium", "low"],
      violation_type: [
        "helmet_off",
        "harness_off",
        "restricted_zone",
        "unsafe_climbing",
        "lifeline_off",
      ],
    },
  },
} as const
