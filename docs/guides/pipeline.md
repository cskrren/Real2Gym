# The Real2Gym pipeline

The authoritative execution rules are the [v5.2 skill](../../skills/real2sim-prompt/SKILL.md). This page is a reader's overview, not a replacement for its gates.

## Step 1: video observations → accepted static scene

1. Record robot/human input, available views, timestamps and trusted measurements.
2. Initialize the first frame: MoGe-3 for a single view, Pi3X jointly for multiple views.
3. Establish semantic instances. Use RGB as the main evidence for mesh shape and occlusion; first-frame point clouds assist depth, orientation and scale. Use at most ten later sparse RGB time indices to reveal surfaces, separating camera and object motion.
4. Build complete task objects, support surfaces and salient background objects. Preserve cavities; do not substitute processed point clouds for all background geometry.
5. Import target robot URDF/MJCF, fit the base/initial joints and cameras, and review multi-view projections. Freeze the accepted scene and its evidence.

## Step 2: demonstrated interaction → native robot execution

| Phase | Work and evidence |
| --- | --- |
| 1 | Receive accepted objects, robot, cameras and initial state |
| 2 | Find changes in real contact, support, grasp and containment relations; choose representative event frames |
| 3 | Recover object/hand/end-effector motion; reuse measured robot state or retarget to selected hardware |
| 4 | Review each event keyframe/view with all five questions; inspect neighborhoods as needed for corrections |
| 5 | Build MuJoCo geometry, cavities, physical properties and actuators; preserve core background display meshes |
| 6 | Execute phases; fix alignment and contact orientation before closure, load bearing, force and friction |
| 7 | Run from final model and initial state; verify task, contacts, stability, geometry and temporal correspondence |
| 8 | Transfer native motion to Blender, refine foreground/background appearance and export Real/Blender/MuJoCo RGB |

Five questions: largest difference; camera alignment; relative object position; penetration/contact; material/texture/light/background realism. A failed visual alignment gate cannot be bypassed with a task-success flag. Neighborhoods locate and regress issues; they do not require a full repeated five-question form on every video frame.

In phase 8, fix geometry and cameras first, then material color/metalness/roughness, texture scale/UV/detail, lighting/environment/exposure, and multi-view previews before increasing render samples. Use licensed assets and record generated texture provenance.

For human input, target hardware is selected in step 1; motion retargeting happens in step 2 phase 3. Try the demonstrated action and station first. If adaptation is necessary, preserve task logic and compare station-preserving and contact-preserving alternatives under contact-stability constraints. Disclose `success_adapted_trajectory` separately from source-faithful reproduction.

## Step 3: accepted scene → augmented simulation family

First probe individual mechanical changes. The tested extremes are sampling references, not a guarantee that every combination inside them works. Sample one to three edits, including single edits. Objects and facilities can change geometry, position and horizontal orientation; support height can change too. Table-mounted arms move with the table; ground-mounted humanoids normally retain the ground reference. Table size is a support constraint, not an independent decorative perturbation.

Retarget and test every mechanical candidate; reduce failed deviations modestly within the declared budget while retaining failure records. For baseline plus N accepted mechanical variants, retain baseline appearance and sample M appearance/environment variants each: `(1+N) × (1+M)`. Deduplicate final parameters, report diversity, and revalidate every child because distractors/background changes can affect physics. The accepted count can be less than the candidate count.

Do not require an augmented scene to match nonexistent augmented Real RGB. Validate its parent-child changes, support, mounting, visual/collision agreement, native outcome and rendered identities instead.

## Feedback and stopping

Steps 1 and 2 use issue-driven local correction and full relevant regression, without a fixed iteration count. Stop on the requested acceptance conditions or an explicit blocker; already accepted nonblocking differences are not endlessly reopened. Step 3 has finite sampling/retry budgets and may retain rejected candidates. Cache reuse must follow actual dependency validity; the unified cache scheduler remains unimplemented.
