import html
import os
import re

import jupytext
import markdown
import requests
from bs4 import BeautifulSoup
from markdown.extensions import fenced_code
from nbformat import read


class NotebookToMedium:
    def __init__(self):
        self.md = markdown.Markdown(extensions=[fenced_code.FencedCodeExtension()])

    def convert_notebook_to_markdown(self, input_notebook, output_markdown):
        """
        Convert a Markdown file to HTML and save it to a file.

        Args:
            input_markdown (str): Path to the input Markdown file.
            output_html (str): Path to the output HTML file.
        """
        with open(input_notebook, "r", encoding="utf-8") as notebook_file:
            notebook = read(notebook_file, as_version=4)

        markdown_text = jupytext.writes(notebook, fmt="markdown")

        # Remove the Jupytext metadata from the Markdown
        markdown_text = re.sub(
            r"---\s+jupyter:\s+\S+.*?---", "", markdown_text, flags=re.DOTALL
        )

        with open(output_markdown, "w", encoding="utf-8") as output_file:
            output_file.write(markdown_text)

    def convert_markdown_to_html(
        self,
        input_markdown,
        output_html,
        nest_as_medium=True,
        transform_pre_code=True,
        add_title_to_pictures=True,
    ):
        """
        Convert a Markdown file to HTML and save it to a file.

        Args:
            input_markdown (str): Path to the input Markdown file.
            output_html (str): Path to the output HTML file.
        """

        with open(input_markdown, "r", encoding="utf-8") as markdown_file:
            markdown_text = markdown_file.read()

        html_text = self.md.convert(markdown_text)

        if nest_as_medium:
            html_text = self.transform_nested_ul_to_medium_nested_list(html_text)

        if transform_pre_code:
            html_text = self.transform_pre_code(html_text)

        if add_title_to_pictures:
            html_text = self.add_title_to_pictures(html_text)

        with open(output_html, "w", encoding="utf-8") as output_file:
            output_file.write(html_text)

    def convert_notebook_to_html(self, input_notebook, output_html):
        """
        Convert a Jupyter notebook to HTML.

        This method performs the conversion by first converting the notebook to Markdown,
            and then converting the Markdown to HTML.
            IMPORTANT: This is to avoid generating binaries, using intermediate Markdown instead
            of converting directly to html with jupytext is purposeful

        Args:
            input_notebook (str): Path to the input Jupyter notebook.
            output_html (str): Path to the output HTML file.
        """
        temp_markdown = "temp_markdown.md"

        # Convert the notebook to Markdown
        self.convert_notebook_to_markdown(input_notebook, temp_markdown)

        # Convert the Markdown to HTML
        self.convert_markdown_to_html(temp_markdown, output_html)

        # Remove the temporary Markdown file
        os.remove(temp_markdown)

    def transform_nested_ul_to_medium_nested_list(self, input_string):
        """
        Transform nested <ul> and <li> tags to a medium.com-friendly format.

        Replaces nested <ul> tags with <br> and <li> tags with '- ' to format them as medium.com lists.

        Args:
            input_string (str): The input HTML string containing nested <ul> and <li> tags.

        Returns:
            str: The transformed HTML string.
        """
        soup = BeautifulSoup(input_string, "html.parser")

        # Find and replace NESTED <ul> and its <li> tags
        for ul1 in soup.find_all("ul"):
            for ul2 in ul1.find_all("ul"):
                replace_string = " ".join(str(item) for item in ul2.contents)
                replace_string = replace_string.replace("<li>", "<br>\n- ").replace(
                    "</li>", ""
                )
                ul2.replace_with(replace_string)

        result = str(soup.prettify())
        result = html.unescape(result)
        return result

    def transform_pre_code(self, input_string):
        """
        Transform <pre> elements with <code> tags inside.

        This function takes an HTML string as input, searches for <pre> elements that contain <code> tags,
        extracts the programming language from the <code> tag's class attribute, and transforms the <pre> element
        with new attributes for Medium.com-friendly code blocks.

        Args:
            input_string (str): The input HTML string.

        Returns:
            str: The transformed HTML string with updated attributes for <pre> elements.
        """
        soup = BeautifulSoup(input_string, "html.parser")
        for pre in soup.find_all("pre"):
            code = pre.find("code")
            if code:
                language_list = code.get("class")
                language = ""
                for item in language_list:
                    if "language-" in item:
                        language = item.replace("language-", "")
                pre["data-code-block-lang"] = language
                pre["data-code-block-mode"] = "2"
                pre["spellcheck"] = "false"
                pre["class"] = "graf--preV2"

        return str(soup.prettify())

    def add_title_to_pictures(self, input_string):
        """
        Add captions to images with titles in the input HTML.

        This function searches for <img> elements with a "title" attribute in the input HTML string
        and adds extra tags to transform them into figures with captions. The title attribute is used
        as the caption text.

        Args:
            input_string (str): The input HTML string containing <img> elements.

        Returns:
            str: The HTML string with captions added to images with titles.
        """
        soup = BeautifulSoup(input_string, "html.parser")
        for img in soup.find_all("img"):
            title = img.get("title")
            if title:
                replace_string = (
                    '<figure tabindex="0" contenteditable="false" data-testid="editorImageParagraph" class="graf graf--figure graf-after--h4">'
                    + '<div class="aspectRatioPlaceholder">'
                    + str(img)
                    + "</div>"
                    + f'<figcaption class="imageCaption" contenteditable="true" data-default-value="Type caption for image (optional)">{title}<br></figcaption>'
                    + " </figure>"
                )
                img.replace_with(replace_string)
        result = str(soup.prettify())
        result = html.unescape(result)
        return result

    def push_to_medium(
        self,
        file_to_upload,
        medium_id,
        token,
        title,
        tag_list,
        publish_status="draft",
        content_format="html",
    ):
        """
        Push an HTML file to Medium as a draft post.

        Args:
            file_to_upload (str): Path to the HTML file to be uploaded.
            id (str): User ID for Medium.
            token (str): Medium API token.
        """
        with open(file_to_upload, "r") as content_text:
            content = content_text.read()

        url = f"https://api.medium.com/v1/users/{medium_id}/posts"

        post_data = {
            "title": title,
            "contentFormat": content_format,
            "content": content,
            "tags": tag_list,
            "publishStatus": publish_status,
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
        }

        response = requests.post(url, headers=headers, json=post_data)

        if response.status_code == 201:
            post_details = response.json()
            print("Draft Post Created Successfully:")
            print("Post Details:")
            print(post_details)
        else:
            print("Failed to create draft post. Status code:", response.status_code)
            print("Response:", response.text)

    def push_ipynb_or_md_to_medium(
        self, input_file, medium_id, token, title, tag_list, publish_status="draft"
    ):
        """
        Convert an .ipynb or .md file to HTML and push to Medium as a draft post.

        Args:
            input_file (str): Path to the .ipynb or .md file to be uploaded.
            id (str): User ID for Medium.
            token (str): Medium API token.
            title (str): Title for the Medium post.
            tag_list (list): List of tags for the Medium post.
            publish_status (str, optional): Publish status (default: 'draft').
        """
        if input_file.lower().endswith(".ipynb"):
            html_output_file = os.path.splitext(input_file)[0] + ".html"
            self.convert_notebook_to_html(input_file, html_output_file)
        elif input_file.lower().endswith(".md"):
            html_output_file = os.path.splitext(input_file)[0] + ".html"
            self.convert_markdown_to_html(input_file, html_output_file)
        else:
            raise ValueError("Input file must be either .ipynb or .md")

        self.push_to_medium(
            html_output_file, medium_id, token, title, tag_list, publish_status
        )
