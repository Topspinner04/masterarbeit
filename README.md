## Usage Guide

Follow these steps to generate and run tasks for a project and specified treatment:

1. **Specifiy treatment**  
   Set project and treatment in `config.py`.

2. **Edit the context and task prompt**  
   Update `user.md` and review the context information in `ref/<project>/docs`.

. **Run the coding agent**  
   Execute: `python main.py`

5. **Review generated output**  
   Modified and newly generated files will be stored in `generated/<project>`.

6. **Switch projects or treatments (optional)**  
   Update the project name and treatment in `config.py`. Make sure that the source files and context information are present in `ref/<project>`.

7. **Regenerate prompts for a new project (optional)**  
   Re-run: `python -m scripts/create_prompt`
