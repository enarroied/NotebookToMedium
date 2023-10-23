# NotebookToMedium

NotebookToMedium is a Python class that allows you to convert Jupyter notebooks (.ipynb) or Markdown files (.md) to HTML and then push the resulting HTML content to Medium as a draft post. This is a convenient way to publish your Jupyter notebooks or Markdown documents on Medium.

## Features

- Conversion of Jupyter notebooks to HTML.
- Conversion of Markdown files to HTML.
- Automatic transformation of nested lists and code blocks for compatibility with Medium.
- Publishing as a draft post on Medium.

## Prerequisites

Before using NotebookToMedium, make sure you have the following installed:

- Python 3.x
- Required Python packages (you can install them using `pip`):
  - jupyter
  - markdown
  - requests
  - jupytext
  - beautifulsoup4

## Installation

You can clone this repository and use the `NotebookToMedium` class in your project. Ensure you meet the prerequisites mentioned above.

```bash
git clone https://github.com/your-username/NotebookToMedium.git
cd NotebookToMedium
```

## Usage

1. Import the `NotebookToMedium` class into your project.

2. Create an instance of the class:

```python
ntm = NotebookToMedium()
```

3. To convert a Jupyter notebook or Markdown file and push it to Medium, use the push_ipynb_or_md_to_medium method. Here's an example:

```python
input_file = "your_notebook.ipynb"  # Provide your input file
medium_id = "your-medium-user-id"  # Your Medium user ID
token = "your-medium-api-token"  # Your Medium API token
title = "Your Post Title"  # Title for the Medium post
tag_list = ["tag1", "tag2"]  # List of tags for the Medium post

ntm.push_ipynb_or_md_to_medium(input_file, medium_id, token, title, tag_list)
```

License

This project is licensed under the MIT License - see the LICENSE file for details.