# UI/UX Engineering Rules

UI changes must be verified through actual application behavior whenever practical.

---

## 1. Inspect Existing UI First

Before modifying UI:

Identify:

- Layout system
- Navigation
- Components
- Theme
- Typography
- State handling
- Responsive behavior
- Existing design system

---

## 2. Preserve Design Language: The Bento Grid Style ("Banto Style")

Inferaxis's official UI/UX design architecture is the **Bento Grid (Banto Style)**.

All new screens, dashboards, and analytical workspaces must follow the Bento style principles:
- **Modular Bento Cells:** Every distinct widget or capability lives in a self-contained card container.
- **Asymmetric Proportions:** Mix 4-column metric counters, 2/3 wide hero blocks, and balanced 3-column cockpits rather than generic uniform tables.
- **Visual Harmony:** Rounded corners (`rounded-2xl` / 16px), subtle 1px border dividers (`border-slate-200/80`), soft pastel icon backgrounds, and gentle drop shadows.
- **Deep Navy Sidebar with Light/Clean Canvas:** High-contrast left navigation rail paired with a scannable, uncluttered workspace canvas.

Follow the existing:

- Typography (Inter for copy, tabular numbers for statistics, JetBrains Mono for code/schemas)
- Spacing (16px / 24px grid gaps)
- Radius (`rounded-2xl` for Bento cards, `rounded-lg` for buttons/inputs, `rounded-full` for status pills)
- Shadows (Soft subtle elevation `shadow-sm`)
- Components (shadcn/ui primitives)
- Color system (Royal Blue CTA, Emerald Success, Purple AI Sparkle, Amber Alerts)
- Interaction patterns (Live agent execution timelines, interactive hover cards)


---

## 3. Avoid UI Clutter

Do not add UI elements merely because they are technically possible.

Every visible element should have a purpose.

Prioritize:

- Clear hierarchy
- Discoverability
- Readability
- Consistent spacing
- Simple workflows

---

## 4. Do Not Assume Visual Success

Code inspection alone cannot guarantee visual correctness.

When practical:

1. Run the application.
2. Navigate to the affected screen.
3. Verify rendering.
4. Verify interactions.
5. Check relevant states.

---

## 5. Responsive Behavior

When relevant, verify:

- Desktop
- Smaller viewport
- Long content
- Empty state
- Error state
- Loading state

---

## 6. Accessibility

Consider:

- Readable contrast
- Keyboard accessibility where applicable
- Clear labels
- Error messages
- Focus states
- Semantic structure

---

## 7. Loading and Error States

Every asynchronous or expensive operation should have appropriate:

- Loading state
- Success state
- Error state
- Empty state where applicable

Do not leave the user with ambiguous UI.

---

## 8. UI Performance

Avoid unnecessary:

- Re-renders
- Expensive calculations
- Duplicate data loading
- Large DOM/component trees
- Repeated model operations

Measure when performance is a concern.

---

## 9. No Fake UX Verification

Do not claim:

"Looks perfect"

based only on generated code.

Report what was actually verified.