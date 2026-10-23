# UI Context

## Theme

The design language is a dark, Codeforces-inspired competitive-programming interface. It uses near-black page backgrounds, layered panels, compact tables, blue links, and rating colors adapted for a dark background. Preserve the existing visual language and CSS conventions when adding new screens.

## Colors

Define and reuse the existing CSS custom properties. Do not introduce replacement tokens or hardcoded colors when an existing token is appropriate.

| Role            | CSS Variable       | Value    |
| --------------- | ------------------ | -------- |
| Page background | `--bg`             | `#0d1117` |
| Surface         | `--panel`          | `#151b23` |
| Primary text    | `--text`           | `#d5dbe4` |
| Muted text      | `--muted`          | `#8793a4` |
| Primary accent  | `--link`            | `#58a6ff` |
| Border          | `--border`         | `#2a3340` |
| Error            | Not defined        | Not defined |
| Success          | Not defined        | Not defined |

## Typography

| Role      | Font                                      | Variable       |
| --------- | ----------------------------------------- | -------------- |
| UI text   | Verdana, Geneva, "DejaVu Sans", sans-serif | Not defined |
| Code/mono | Not defined                               | Not defined |

## Border Radius

| Context           | Class or value |
| ----------------- | -------------- |
| Inline / small UI | `3px`          |
| Cards / panels    | `4px`          |
| Modals / overlays | Not defined    |

## Component Library

The frontend uses Angular components and custom CSS. No separate UI component library or icon library is configured in the current dependencies. Existing shared styles include roundbox panels, problem tables, tags, pagination, forms, and notices. Reuse these patterns where appropriate.

## Layout Patterns

- Problemset: main content with a 290px sidebar and a 16px gap; collapse to a single column at viewport widths below 900px.
- Panels: use the existing `roundbox` structure with a caption and body.
- Tables: use compact rows, alternating backgrounds, horizontal overflow handling, and hover states.
- Forms: use the existing dark input, select, textarea, button, and focus styles.
- Feedback: use the existing notice, empty-state, and muted-text patterns.

## Icons

No icon library is currently configured in the frontend dependencies. Preserve existing conventions and do not introduce an icon library without approval.
