import ast
import argparse
import os
from pathlib import Path

class DocGenerator:
    def __init__(self, filePath):
        self.filePath = filePath

    def extractFunctions(self):
        """Extract functions and their docstrings from the Python file."""
        with open(self.filePath, 'r') as file:
            fileContent = file.read()

        # Parse the file content into an AST
        tree = ast.parse(fileContent)

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):  # Check if it's a function definition
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node)
                })
        return functions

    def generateDocs(self, outputFormat="markdown"):
        """Generate the documentation based on the extracted functions."""
        functions = self.extractFunctions()

        if outputFormat == "markdown":
            return self.generateMarkdown(functions)
        # You can add other formats like HTML, plain text, etc.

    def generateMarkdown(self, functions):
        """Generate a Markdown document from the extracted functions."""
        doc = "# Auto-generated Documentation\n\n"
        for func in functions:
            doc += f"## Function: {func['name']}\n\n"
            doc += f"**Arguments:** {', '.join(func['args'])}\n\n"
            doc += f"**Docstring:**\n\n"
            doc += f"python\n{func['docstring']}\n\n\n"
        return doc

def parseArguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate documentation for Python functions with docstrings.")
    parser.add_argument('filePath', help="The path to the Python file to document.")
    return parser.parse_args()

def getServiceName(file_path, serviceIndex=1):
    """Extract the main service name from the given file path."""
    path_parts = Path(file_path).parts
    return path_parts[serviceIndex]

def main():
    args = parseArguments()

    filePath = args.filePath
    service = getServiceName(filePath)
    outputDir = os.path.join(os.getcwd(), 'docs')
    outputFile = os.path.join(outputDir, f'{service}_api.md')

    docGenerator = DocGenerator(filePath)
    markdownDoc = docGenerator.generateDocs(outputFormat="markdown")

    with open(outputFile, 'w') as f:
        f.write(markdownDoc)

    print(f"Documentation generated and saved to {outputFile}")

if __name__ == "__main__":
    main()
