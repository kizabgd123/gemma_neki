# Design System: Kiza Portfolio (Extracted)

This design system is harvested from [kiza-portfolio.pages.dev](https://kiza-portfolio.pages.dev/). It features a "Premium Tech" aesthetic: dark backgrounds, high-contrast typography, and cyan accents.

## Visual Profile
- **Style**: Modern Dark, Tech-focused
- **Theme**: Deep space black with glowing cyan interactive elements.

## Design Tokens

<!-- STITCH_TOKENS_START -->
{
  "colors": {
    "primary": "#22d3ee",
    "primary-foreground": "#050505",
    "secondary": "rgba(6, 182, 212, 0.2)",
    "secondary-foreground": "#22d3ee",
    "background": "#050505",
    "foreground": "#e4e4e7",
    "card": "#09090b",
    "card-foreground": "#e4e4e7",
    "muted": "#27272a",
    "muted-foreground": "#a1a1aa",
    "accent": "rgba(34, 211, 238, 0.1)",
    "accent-foreground": "#22d3ee",
    "border": "#18181b",
    "input": "#18181b",
    "ring": "#22d3ee"
  },
  "typography": {
    "fonts": {
      "sans": "Inter, sans-serif",
      "heading": "'Space Grotesk', sans-serif",
      "mono": "'JetBrains Mono', monospace"
    },
    "sizes": {
      "xs": "12px",
      "sm": "14px",
      "base": "16px",
      "lg": "18px",
      "xl": "20px",
      "2xl": "24px",
      "3xl": "30px",
      "4xl": "36px",
      "5xl": "48px",
      "hero": "96px"
    }
  },
  "rounding": {
    "none": "0",
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px"
  },
  "spacing": {
    "px": "1px",
    "0": "0",
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "8": "32px",
    "10": "40px",
    "12": "48px"
  },
  "shadows": {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "cyan": "0 0 20px rgba(34, 211, 238, 0.3)"
  }
}
<!-- STITCH_TOKENS_END -->

## Component Guidelines

### Buttons
- **Shape**: Rounded (12px)
- **Hover**: Increase opacity of cyan glow or shift background to solid primary.
- **Typography**: Semibold Inter.

### Cards
- **Background**: Subtle gray (#09090b) or semi-transparent over dark bg.
- **Border**: Thin #18181b border.
- **Shadow**: Subtle on hover.

### Typography Scales
- **Hero**: 96px Space Grotesk, Bold.
- **Body**: 16px Inter, Regular.
- **Navigation**: 14px Inter, Medium.
