from pathlib import Path

candidates = list(Path(".").rglob("DashArena.java"))
if len(candidates) != 1:
    raise SystemExit(f"Expected one DashArena.java, found {candidates}")
p = candidates[0]
s = p.read_text()

replacements = [
    ("    private final List<Wall> walls = new ArrayList<>();\n",
     "    private final List<Wall> walls = new ArrayList<>();\n    private final List<WallBlock> pendingPhysicalBlocks = new ArrayList<>();\n"),
    ("    private void spawnWall() {\n        class_5819 random = world.method_8409();",
     "    private void spawnWall() {\n        pendingPhysicalBlocks.clear();\n        class_5819 random = world.method_8409();"),
    ("        if (!blocks.isEmpty()) walls.add(new Wall(blocks, platforms, hazards, end, world));",
     "        if (!blocks.isEmpty()) walls.add(new Wall(blocks, platforms, hazards, List.copyOf(pendingPhysicalBlocks), end, world));"),
    ("        class_8115 display = (class_8115) class_1299.field_42460.method_5883(world);\n        if (display == null) return;",
     "        class_8115 display = (class_8115) class_1299.field_42460.method_5883(world);\n        if (display == null) return;\n        pendingPhysicalBlocks.add(new WallBlock(pos, state));"),
    ("    private record PlatformTile(class_243 position, class_2680 state) {}",
     "    private record PlatformTile(class_243 position, class_2680 state) {}\n    private record WallBlock(class_243 position, class_2680 state) {}"),
    ("        private final List<class_8115> hazards;\n        private final Map<class_2338, class_2680> originalBlocks = new HashMap<>();\n        private Set<class_2338> activePlatformBlocks = new HashSet<>();",
     "        private final List<class_8115> hazards;\n        private final List<WallBlock> physicalBlocks;\n        private final Map<class_2338, class_2680> originalBlocks = new HashMap<>();\n        private Set<class_2338> activePlatformBlocks = new HashSet<>();\n        private Set<class_2338> activeWallBlocks = new HashSet<>();"),
    ("        Wall(List<class_8115> blocks, List<PlatformTile> platforms, List<class_8115> hazards,\n             class_243 position, class_3218 world) {",
     "        Wall(List<class_8115> blocks, List<PlatformTile> platforms, List<class_8115> hazards,\n             List<WallBlock> physicalBlocks, class_243 position, class_3218 world) {"),
    ("            this.hazards = hazards;\n            this.position = position;",
     "            this.hazards = hazards;\n            this.physicalBlocks = physicalBlocks;\n            this.position = position;"),
    ("            updatePhysicalPlatforms();\n        }\n\n        void move(",
     "            updatePhysicalPlatforms();\n            updatePhysicalWallBlocks();\n        }\n\n        void move("),
    ("            updatePhysicalPlatforms();\n            for (class_3222 player : riding) {",
     "            updatePhysicalPlatforms();\n            updatePhysicalWallBlocks();\n            for (class_3222 player : riding) {"),
    ("        private class_243 initialPosition = class_243.field_1353;\n",
     """        private void updatePhysicalWallBlocks() {
            Set<class_2338> next = new HashSet<>();
            Map<class_2338, class_2680> desired = new HashMap<>();
            class_243 offset = position.method_1020(initialPosition);
            for (WallBlock tile : physicalBlocks) {
                class_243 p = tile.position().method_1019(offset);
                class_2338 bp = class_2338.method_49637(p.field_1352, p.field_1351, p.field_1350);
                next.add(bp);
                desired.put(bp, tile.state());
            }
            for (class_2338 old : activeWallBlocks) {
                if (!next.contains(old)) {
                    class_2680 original = originalBlocks.get(old);
                    if (original != null) world.method_8652(old, original, class_2248.field_31036);
                }
            }
            for (Map.Entry<class_2338, class_2680> entry : desired.entrySet()) {
                class_2338 pos = entry.getKey();
                originalBlocks.putIfAbsent(pos, world.method_8320(pos));
                class_2680 original = originalBlocks.get(pos);
                // La pared es un obstáculo temporal: debe verse incluso si cruza
                // bloques del carril. Guardamos el estado original y lo restauramos
                // cuando la pared avanza o termina.
                if (original != null && !world.method_8320(pos).equals(entry.getValue())) {
                    world.method_8652(pos, entry.getValue(), class_2248.field_31022);
                }
            }
            activeWallBlocks = next;
        }

        private class_243 initialPosition = class_243.field_1353;
"""),
    ("            activePlatformBlocks.clear();\n        }",
     "            activePlatformBlocks.clear();\n            activeWallBlocks.clear();\n        }")
]


replacements.extend([
    ("        travel = start.method_1020(end).method_1029();",
     "        travel = end.method_1020(start).method_1029();"),
    ("        running = true;\n",\n     "        running = true;\n        spawnWall(); // Show the first wall immediately, not after the interval.\n"),\n    ("        if (!blocks.isEmpty()) walls.add(new Wall(blocks, platforms, hazards, List.copyOf(pendingPhysicalBlocks), end, world));",
     "        if (!blocks.isEmpty() || !pendingPhysicalBlocks.isEmpty()) walls.add(new Wall(blocks, platforms, hazards, List.copyOf(pendingPhysicalBlocks), end, world));"),
    ("        class_8115 display = (class_8115) class_1299.field_42460.method_5883(world);\n        if (display == null) return;\n        pendingPhysicalBlocks.add(new WallBlock(pos, state));",
     "        pendingPhysicalBlocks.add(new WallBlock(pos, state));\n        class_8115 display = (class_8115) class_1299.field_42460.method_5883(world);\n        if (display == null) return;"),
    ("""        class_243 fromStart = pos.method_1020(start);
        class_243 line = end.method_1020(start);
        double lengthSq = line.method_1027();
        double t = Math.max(0, Math.min(1, fromStart.method_1026(line) / lengthSq));
        class_243 nearest = start.method_1019(line.method_1021(t));
        return pos.method_1022(nearest) <= width / 2.0;""",
     """        // La anchura se mide en horizontal: saltar no debe eliminar al jugador.
        class_243 fromStart = new class_243(pos.field_1352 - start.field_1352, 0, pos.field_1350 - start.field_1350);
        class_243 line = new class_243(end.field_1352 - start.field_1352, 0, end.field_1350 - start.field_1350);
        double lengthSq = line.method_1027();
        if (lengthSq < 1.0E-6) return false;
        double length = Math.sqrt(lengthSq);
        double t = fromStart.method_1026(line) / lengthSq;
        double endMargin = 4.0 / length;
        if (t < -endMargin || t > 1.0 + endMargin) return false;
        double nearestX = start.field_1352 + line.field_1352 * t;
        double nearestZ = start.field_1350 + line.field_1350 * t;
        double dx = pos.field_1352 - nearestX;
        double dz = pos.field_1350 - nearestZ;
        return dx * dx + dz * dz <= Math.pow(width / 2.0 + 1.0, 2);""")
])

for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match ({count}): {old[:90]!r}")
    s = s.replace(old, new)

# A display entity may fail to spawn. Keep physical blocks regardless, but
# only register a hazard when an entity was actually appended to "blocks".
import re
pattern = r"(?m)^(\s*)addDisplay\(blocks,\s*pos,\s*primary\);\s*\n\1hazards\.add\(blocks\.get\(blocks\.size\(\)\s*-\s*1\)\);"
replacement = r"\1int previousSize = blocks.size();\n\1addDisplay(blocks, pos, primary);\n\1if (blocks.size() > previousSize) {\n\1    hazards.add(blocks.get(blocks.size() - 1));\n\1}"
s, changed = re.subn(pattern, replacement, s)
if changed != 1 and "previousSize = blocks.size()" not in s:
    raise SystemExit(f"Expected one wall hazard registration, patched {changed}")

\n# Use the documented update flag 3 (NOTIFY_NEIGHBORS | NOTIFY_LISTENERS)
# for temporary wall blocks and their restoration, ensuring client chunk updates.
s = s.replace("world.method_8652(old, original, class_2248.field_31036)", "world.method_8652(old, original, 3)")
s = s.replace("world.method_8652(pos, original, class_2248.field_31036)", "world.method_8652(pos, original, 3)")
s = s.replace("world.method_8652(pos, entry.getValue(), class_2248.field_31022)", "world.method_8652(pos, entry.getValue(), 3)")

p.write_text(s)
print("Added temporary physical wall blocks, safe display-entity fallback, and guarded hazard registration.")
