import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-full text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-chelsea-gold disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-chelsea-blue text-white hover:bg-[#0456b5]",
        gold: "bg-chelsea-gold text-chelsea-navy hover:brightness-110",
        ghost: "bg-transparent text-foreground hover:bg-muted",
        outline: "border border-border bg-card/40 hover:bg-muted",
      },
      size: {
        default: "h-10 px-4",
        sm: "h-8 px-3 text-xs",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants>;

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
