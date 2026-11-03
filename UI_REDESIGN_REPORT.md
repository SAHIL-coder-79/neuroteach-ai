# NEUROTEACH AI — UI REDESIGN & DESIGN SYSTEM REPORT

**Audit Date**: 2026-11-03  
**Visual Identity**: Premium Deep Midnight & Glassmorphic EdTech SaaS Platform  

---

## 1. Visual Direction & Palette

The design was updated from flat, generic dark cards to a multi-layered, deep midnight visual aesthetic:

| Color Token | Hex Value | Usage |
| :--- | :--- | :--- |
| **Deep Background** (`bg-base`) | `#080B16` | Main viewport canvas with subtle radial accent glow overlays. |
| **Glass Surface** (`bg-surface`) | `#101629` | Translucent glassmorphic cards with `backdrop-filter: blur(16px)`. |
| **Elevated Glass** (`bg-raised`) | `#18213D` | Elevated interactive cards with inner highlight borders. |
| **Electric Violet Accent** | `#8B5CF6` / `#7C3AED` | Primary brand actions, key buttons, and glow shadows. |
| **Cyan Highlight** | `#67E8F9` | Informational callouts, active sub-status indicators, and telemetry. |
| **Border Glass** | `rgba(255, 255, 255, 0.12)` | Crisp, translucent glass borders giving depth without visual noise. |

---

## 2. Reusable Design Components

1. **`glass-panel`**:
   - Background: `rgba(16, 22, 41, 0.70)`
   - Backdrop filter: `blur(16px)`
   - Border: `1px solid rgba(255, 255, 255, 0.10)`
   - Shadow: `0 8px 32px 0 rgba(0, 0, 0, 0.35)`
2. **`glass-panel-elevated`**:
   - Background: `rgba(24, 33, 61, 0.75)`
   - Backdrop filter: `blur(20px)`
   - Border: `1px solid rgba(255, 255, 255, 0.14)`
   - Inset highlight: `inset 0 1px 0 0 rgba(255, 255, 255, 0.10)`
3. **`card-hover-3d`**:
   - Subtle 3D lift: `transform: translateY(-3px) scale(1.008)`
   - Soft glow elevation: `0 16px 40px -10px rgba(0, 0, 0, 0.5), 0 0 25px -5px rgba(139, 92, 246, 0.25)`

---

## 3. Responsive Behavior Across Breakpoints

- **Desktop ($\ge 1280\text{px}$)**: Full multi-column dashboard with side-by-side visual graph lab and dual diagnostic ledger.
- **Tablet / Laptop ($768\text{px} - 1279\text{px}$)**: Fluid grid collapse with collapsible sidebar (compact 20px icon rail).
- **Mobile ($<768\text{px}$)**: Full-width stacked layout, wrapped header items, touch-optimized input targets.

