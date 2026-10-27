import React from "react";
import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

export interface Step {
  id: string;
  label: string;
}

export interface ProgressStepperProps {
  steps: Step[];
  currentStepIndex: number;
  className?: string;
}

export function ProgressStepper({ steps, currentStepIndex, className }: ProgressStepperProps) {
  return (
    <div className={cn("flex items-center gap-2 w-full overflow-x-auto py-2", className)}>
      {steps.map((step, idx) => {
        const isComplete = idx < currentStepIndex;
        const isCurrent = idx === currentStepIndex;
        const isPending = idx > currentStepIndex;

        return (
          <React.Fragment key={step.id}>
            <div className="flex items-center gap-1.5 shrink-0">
              {isComplete && <CheckCircle2 className="w-4 h-4 text-success" />}
              {isCurrent && <Loader2 className="w-4 h-4 text-accent animate-spin" />}
              {isPending && <Circle className="w-4 h-4 text-text-tertiary" />}
              <span
                className={cn(
                  "text-xs font-medium",
                  isComplete && "text-text-primary",
                  isCurrent && "text-accent font-semibold",
                  isPending && "text-text-tertiary"
                )}
              >
                {step.label}
              </span>
            </div>
            {idx < steps.length - 1 && (
              <div
                className={cn(
                  "h-px w-6 sm:w-10 shrink-0",
                  idx < currentStepIndex ? "bg-success" : "bg-border"
                )}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
