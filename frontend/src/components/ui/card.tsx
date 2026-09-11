import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div
    className={twMerge(
      clsx(
        "rounded-xl border border-slate-200/90 bg-white text-slate-900 shadow-xs hover:border-slate-300 transition-colors",
        className
      )
    )}
    {...props}
  >
    {children}
  </div>
);

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={twMerge(clsx("flex flex-col space-y-1.5 p-5 border-b border-slate-100", className))} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => (
  <h3 className={twMerge(clsx("text-base font-semibold text-slate-900 tracking-tight", className))} {...props}>
    {children}
  </h3>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={twMerge(clsx("p-5 pt-4", className))} {...props}>
    {children}
  </div>
);
