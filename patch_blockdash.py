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
                if (original != null && original.method_26215()
                    && !world.method_8320(pos).equals(entry.getValue())) {
                    world.method_8652(pos, entry.getValue(), class_2248.field_31036);
                }
            }
            activeWallBlocks = next;
        }

        private class_243 initialPosition = class_243.field_1353;
"""),
    ("            activePlatformBlocks.clear();\n        }",
     "            activePlatformBlocks.clear();\n            activeWallBlocks.clear();\n        }")
]

for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match ({count}): {old[:90]!r}")
    s = s.replace(old, new)

p.write_text(s)
print("Added temporary physical wall blocks that move with each wall and restore original terrain.")
