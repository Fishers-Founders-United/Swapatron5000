# Bin Label Design Guidelines

This document defines the visual language for all bin labels used throughout the Swapatron5000 system. Each bin type has a **text label** and an **icon** that should be displayed together on physical signage and in the web UI.

---

## Bin Types

| Bin ID | Text Label | Icon | Description |
|--------|------------|------|-------------|
| `recycling` | Recycling | ![recycling icon](https://raw.githubusercontent.com/Fishers-Founders-United/Swapatron5000/main/assets/icons/recycling.svg) | Materials that can be re‑processed into new products. |
| `compost` | Compost | ![compost icon](https://raw.githubusercontent.com/Fishers-Founders-United/Swapatron5000/main/assets/icons/compost.svg) | Organic waste suitable for composting. |
| `landfill` | Landfill | ![landfill icon](https://raw.githubusercontent.com/Fishers-Founders-United/Swapatron5000/main/assets/icons/landfill.svg) | Non‑recyclable, non‑compostable waste. |
| `hazardous` | Hazardous | ![hazardous icon](https://raw.githubusercontent.com/Fishers-Founders-United/Swapatron5000/main/assets/icons/hazardous.svg) | Materials requiring special handling (e.g., batteries, chemicals). |

> **Tip:** When adding a new bin type, follow the same pattern: create an SVG icon (24×24 px, solid fill, high contrast) and place it in `assets/icons/`.

---

## Icon Guidelines

1. **Size** – Icons must be 24 × 24 px for consistency across platforms.
2. **Color** – Use the primary brand color `#0066CC` for the icon fill. Ensure a minimum contrast ratio of 4.5:1 against the background.
3. **Format** – SVG is required for scalability. Include a fallback PNG (32 × 32 px) in the same directory for legacy browsers.
4. **Naming** – File names should be kebab‑case matching the bin ID, e.g., `recycling.svg`.
5. **Accessibility** – Provide an `aria-label` attribute when rendering the icon in HTML, e.g., `<svg aria-label="Recycling icon" …>`.

---

## Usage Examples

### Markdown
```markdown
![Recycling](assets/icons/recycling.svg) **Recycling**
```

### HTML (Web UI)
```html
<span class="bin-label">
  <svg class="icon" aria-label="Recycling icon" role="img">
    <use href="/assets/icons/recycling.svg#icon" />
  </svg>
  Recycling
</span>
```

### Physical Signage
Print the SVG at 300 dpi on a matte white background. The icon should occupy the left third of the label, with the text right‑aligned.

---

## Adding New Bins
1. Create an SVG icon following the guidelines above.
2. Add the SVG (and optional PNG) to `assets/icons/`.
3. Update the table in this document with the new row.
4. If the bin is used in the UI, add the corresponding entry to the `binTypes` enum in the codebase.

---

## References
- [Design System – Color Palette](../design/color_palette.md)
- [Accessibility Guidelines](../design/accessibility.md)

---

*Document version: 1.0 – November 2026*