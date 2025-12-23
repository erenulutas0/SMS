import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
    return twMerge(clsx(inputs))
}

// Helper to safely parse dates (handles ADB numeric strings)
export function parseDate(ts) {
    if (!ts) return new Date();
    // If it's a string of digits, parse as INT first (ADB returns millis as string)
    if (typeof ts === 'string' && /^\d+$/.test(ts)) {
        return new Date(parseInt(ts, 10));
    }
    return new Date(ts);
}

// Native Date Formatter to replace date-fns
export function formatDate(dateOrTs, fmt) {
    const d = parseDate(dateOrTs);
    if (fmt === 'HH:mm') {
        return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    }
    if (fmt === 'd MMM HH:mm') {
        // toLocaleString combines date and time
        return d.toLocaleString('tr-TR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    }
    if (fmt === 'HH:mm:ss') {
        return d.toLocaleTimeString('tr-TR');
    }
    return d.toLocaleString('tr-TR');
}
