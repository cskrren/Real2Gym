# Accepted simulation → scene family

Use $real2sim-prompt to run Real2Gym step 3 on /absolute/path/accepted-scene and its native evidence.

Keep the accepted target hardware. Request N=3 mechanical variants and M=2 appearance variants per parent, in addition to each baseline; use seed 42. Limit this batch to 12 initial mechanical candidates and 3 shrink retries per failed candidate. These are example user budgets, not universal defaults; report if fewer variants pass.

Probe individual task-object/facility geometry, position, horizontal orientation and support-height changes. Randomly choose one to three edits per candidate, allowing single edits. On failure retain the same edit set and modestly shrink deviations before revalidation. Deduplicate final candidates. Table-mounted arms follow table height; ground-mounted humanoids normally retain the ground reference.

For baseline plus accepted mechanical parents, retain original appearance and add foreground/background textures, realistic distractors, complete backgrounds and moderate lights. Preserve full display assets in Blender and MuJoCo. Revalidate every child and report task outcomes, parent-child differences, diversity and failure reasons. Do not add object-category replacement, tipped containers or altered door initial angles by default. Export Blender/MuJoCo comparisons; original Real RGB is a task reference, not paired augmented ground truth.
