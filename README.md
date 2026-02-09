```text
1. Edit user prompt in user.md and check context information in context/"project"/architecture_documentation.md
2. Use create_prompt.py to create task (user+context) prompt.
3. Run main.py to run coding agent with prompts and tools.
4. Modified and generated files will be stored in generated/"project".
5. Project can be changed in config. Make sure the source files for the project are present in ref/"project" and documentation is present in context/"project"/architecture_documentation.md.
6. Rerun create_prompts.py to update prompts for the new project.
```
