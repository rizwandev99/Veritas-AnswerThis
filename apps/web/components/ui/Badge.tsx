import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "outline" | "supported" | "partial" | "unsupported" | "unchecked";
  size?: "sm" | "md";
  interactive?: boolean;
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "default", size = "sm", interactive = false, children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center font-medium rounded-full transition-colors select-none";

    const variants = {
      default: "bg-surface-elevated text-text-secondary border border-border",
      outline: "border border-border text-text-primary bg-transparent",
      info: "bg-info-surface text-info border border-info-border",
      success: "bg-success-surface text-success border border-success-border",
      warning: "bg-warning-surface text-warning border border-warning-border",
      danger: "bg-danger-surface text-danger border border-danger-border",
      // Academic Verification Semantics
      supported: "bg-success-surface text-success border border-success-border",
      partial: "bg-warning-surface text-warning border border-warning-border",
      unsupported: "bg-danger-surface text-danger border border-danger-border",
      unchecked: "bg-surface-elevated text-text-tertiary border border-border",
    };

    const sizes = {
      sm: "text-xs px-2 py-0.5 gap-1",
      md: "text-xs px-2.5 py-1 gap-1.5",
    };

    const interactiveStyles = interactive
      ? "cursor-pointer hover:opacity-80 active:scale-95"
      : "";

    return (
      <span
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], interactiveStyles, className)}
        {...props}
      >
        {children}
      </span>
    );
  }
);
Badge.displayName = "Badge";
