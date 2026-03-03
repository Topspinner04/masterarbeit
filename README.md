## Usage Guide

Follow these steps to generate and run tasks for a project and specified treatment:

1. **Specifiy treatment**  
   Set project and treatment in `config.py`.

2. **Edit the context and task prompt**  
   Update `task.md` and `context.md` and review the context information in `ref/<project>/docs`.

3. **Generate the user prompt**  
   Run: `python -m scripts/create_prompt`  
   This combines the context and task prompt into a single user prompt for the specified treatment.

4. **Run the coding agent**  
   Execute: `python main.py`

5. **Review generated output**  
   Modified and newly generated files will be stored in `generated/<project>`.

6. **Switch projects or treatments (optional)**  
   Update the project name and treatment in `config.py`. Make sure that the source files and context information are present in `ref/<project>`.

7. **Regenerate prompts for a new project (optional)**  
   Re-run: `python -m scripts/create_prompt`
