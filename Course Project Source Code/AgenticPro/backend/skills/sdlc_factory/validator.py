from typing import Any


class SDLCFactoryValidator:
    """
    Validates the structure, integrity, and deliverable completeness of SDLC project artifacts.
    """

    REQUIRED_TOP_KEYS = ["user_stories", "architecture", "code_files"]

    def validate(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        for k in self.REQUIRED_TOP_KEYS:
            if k not in data or not data[k]:
                return False

        stories = data.get("user_stories")
        if not isinstance(stories, list) or len(stories) == 0:
            return False

        for story in stories:
            if not isinstance(story, dict):
                return False
            if "title" not in story or "acceptance_criteria" not in story:
                return False

        arch = data.get("architecture")
        if not isinstance(arch, dict) or "system_overview" not in arch:
            return False

        files = data.get("code_files")
        if not isinstance(files, list) or len(files) < 2:
            return False

        has_source = False
        has_test = False
        for f in files:
            if not isinstance(f, dict):
                return False
            if "filepath" not in f or "content" not in f:
                return False
            ft = f.get("file_type", "")
            if ft == "source":
                has_source = True
            elif ft == "test":
                has_test = True

        return has_source and has_test
