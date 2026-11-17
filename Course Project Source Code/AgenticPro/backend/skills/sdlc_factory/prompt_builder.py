class SDLCFactoryPromptBuilder:
    """
    Builds comprehensive multi-stage SDLC generation prompts (Requirement -> Tested Implementation).
    """

    def build(
        self,
        project_name: str,
        requirement_text: str,
        target_language: str = "python",
        framework: str = "fastapi",
        architecture_style: str = "clean_architecture",
    ) -> str:
        return f"""You are a Principal Software Architect and Lead Systems Engineer operating an Autonomous SDLC Factory.
Transform the following high-level software requirements into a complete, modular, production-ready, and fully-tested software project.

PROJECT NAME: {project_name}
TARGET LANGUAGE: {target_language}
FRAMEWORK: {framework}
ARCHITECTURE STYLE: {architecture_style}

USER REQUIREMENTS SPECIFICATION:
\"\"\"
{requirement_text}
\"\"\"

Produce a comprehensive JSON response matching this exact structure:
{{
  "user_stories": [
    {{
      "id": "US-01",
      "title": "Story Title",
      "as_a": "System Client / User",
      "i_want": "Specific capability",
      "so_that": "Clear business value",
      "acceptance_criteria": ["Given X when Y then Z", "Criterion 2"],
      "priority": "High"
    }}
  ],
  "architecture": {{
    "system_overview": "Architectural breakdown of layers and responsibilities",
    "architecture_style": "{architecture_style}",
    "components": [
      {{
        "name": "CoreService",
        "responsibility": "Encapsulates business rules and state",
        "interface_methods": ["execute(input)", "query(id)"]
      }}
    ],
    "data_schemas": [
      {{"entity": "EntityName", "fields": "id: str, value: int, created_at: float"}}
    ],
    "api_endpoints": [
      {{"method": "POST", "path": "/api/resource", "description": "Execute core logic"}}
    ]
  }},
  "code_files": [
    {{
      "filepath": "src/models.py",
      "file_type": "source",
      "language": "python",
      "description": "Domain entities and data structures",
      "content": "from pydantic import BaseModel\\n..."
    }},
    {{
      "filepath": "src/service.py",
      "file_type": "source",
      "language": "python",
      "description": "Core business logic implementation",
      "content": "class Service:\\n    ..."
    }},
    {{
      "filepath": "tests/test_service.py",
      "file_type": "test",
      "language": "python",
      "description": "Automated unit test suite verifying acceptance criteria",
      "content": "def test_normal_operation():\\n    ..."
    }}
  ]
}}
"""
