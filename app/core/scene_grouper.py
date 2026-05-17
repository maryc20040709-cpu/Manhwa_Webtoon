class SceneGrouper:
    def __init__(self, row_threshold=50):
        # Panels within this many pixels vertically = same scene
        self.row_threshold = row_threshold

    def process_scenes(self, panels):
        # Sort panels by vertical position (top to bottom)
        return sorted(panels, key=lambda p: p[1])

    def group_scenes(self, panels):
        if not panels:
            return {}

        sorted_panels = self.process_scenes(panels)
        scenes = {}
        scene_index = 1
        current_scene = [sorted_panels[0]]
        current_y = sorted_panels[0][1]

        for panel in sorted_panels[1:]:
            panel_y = panel[1]
            if abs(panel_y - current_y) <= self.row_threshold:
                # Same row = same scene
                current_scene.append(panel)
            else:
                # New row = new scene
                scenes[f"scene_{scene_index}"] = current_scene
                scene_index += 1
                current_scene = [panel]
                current_y = panel_y

        # Add last scene
        scenes[f"scene_{scene_index}"] = current_scene
        return scenes
