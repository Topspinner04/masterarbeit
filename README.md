## Usage Guide

Follow these steps to generate and run tasks for a project:

1. **Edit the user prompt**  
   Update `user.md` and review the context information in  
   `context/<project>/architecture_documentation.md`.

2. **Generate the task prompt**  
   Run: `python -m create_prompt.py`  
   This combines the user prompt and context into a single task prompt.

3. **Run the coding agent**  
   Execute: `python main.py`

4. **Review generated output**  
   Modified and newly generated files will be stored in:  
   `generated/<project>`

5. **Switch projects (optional)**  
   Update the project name in `config`. Make sure that:

   - Source files are present in `ref/<project>`
   - Documentation is present in `context/<project>/architecture_documentation.md`

6. **Regenerate prompts for a new project**  
   Re-run: `python -m create_prompt.py`
