import React from "react";
import { cn } from "@/lib/utils";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "ghost" | "outline" | "secondary";
  size?: "sm" | "md" | "lg";
  "aria-label": string;
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant = "ghost", size = "md", "aria-label": ariaLabel, children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center rounded-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:opacity-50";

    const variants = {
      ghost: "text-text-secondary hover:text-text-primary hover:bg-surface-elevated",
      outline: "border border-border bg-transparent text-text-primary hover:bg-surface-elevated",
      secondary: "bg-surface-elevated text-text-primary hover:bg-border/60",
    };

    const sizes = {
      sm: "h-7 w-7 text-xs",
      md: "h-8 w-8 text-sm",
      lg: "h-10 w-10 text-base",
    };

    return (
      <button
        ref={ref}
        aria-label={ariaLabel}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);
IconButton.displayName = "IconButton";
