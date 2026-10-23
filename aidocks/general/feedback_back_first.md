---
name: feedback_back_first
description: "Every menu with a way back has a Back row, always the first row and the one it opens on, Settings and the volume levels included; menus whose first row is already their way back keep it."
metadata:
  node_type: memory
  type: feedback
---

Every menu that can be left by going back has a **Back** row, and it is **always the first row**. Anything else that should come first comes straight after it.

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22.

**How to apply:**
- It holds for screens not built on the shared menu code too, such as an F1 key bindings screen: Back is its first row and it opens on it, with Enter there going back as Escape does.
- The menu opens on Back, never on another row. A volume's levels open on Back, not on the level it is at.
- Menus whose first row is already their way back keep it, such as a main menu's Quit, a pause menu's Resume, or a yes-or-no question's No.
- The original's own menus are spoken recordings answered by swipes, not lists ([[project_original_behaviour]]). How they become the port's menus is for the menus plan; this rule applies to every list menu the port adds.
