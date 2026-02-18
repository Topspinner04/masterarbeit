## Usage Guide

Follow these steps to generate and run tasks for a specified treatment:

1. **Specifiy treatment**  
   Set treatment to `treatment_a` or `treatment_b` in `config.py`.

2. **Edit the user prompt**  
   Update `user.md` and review the context information for the specified treatment in  
   `context/<project>/`.

3. **Generate the task prompt**  
   Run: `python -m create_prompt.py`  
   This combines the task prompt and context into a single user prompt for the specified treatment.

4. **Run the coding agent**  
   Execute: `python main.py`

5. **Review generated output**  
   Modified and newly generated files will be stored in:  
   `generated/<project>`

6. **Switch projects or treatments (optional)**  
   Update the project name and treatment in `config.py`. Make sure that:

   - Source files are present in `ref/<project>`
   - Documentation for specified treatment is present in `context/<project>/`

7. **Regenerate prompts for a new project (optional)**  
   Re-run: `python -m create_prompt.py`
