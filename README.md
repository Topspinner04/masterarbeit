## What is this repository about?
By executing `main.py`, an agent will be tasked with the specified prompts. It will attempt to implement the features described in the prompt on the reference files in `ref/<project>`. Afterwards, the edited files will be copied to `generated` for further analysis and the `ref/<project>` will be reset to the last commit. This is handled via git, the repository is a submodule. You can set different treatments (i.e. different prompt, agent and context configurations) in `config.py`. 

## Usage Guide

Follow these steps to generate and run tasks for a project and specified treatment:

1. **Specifiy treatment**  
   Set project and treatment in `config.py`.

2. **Edit the context and task prompt**  
   Update `user.md` for specified treatment.

3. **Update architecture documentation and create vector store (optional)**
   Run `build_index.py` to build the vector store to embedd the architecture documentation for the RAG agent. Make sure the architecture documentation fits the project. This only has to be done once per project, the vector store will be overwritten.

3. **Run the coding agent**  
   Execute: `python main.py`

4. **Review generated output**  
   Modified and newly generated files will be stored in `generated/<project>`.

5. **Switch projects or treatments (optional)**  
   Update the project name and treatment in `config.py`. Make sure that the source files are added as submodule in `ref/<project>`.
