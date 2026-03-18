import json
import html
from urllib.parse import urlencode

base_url = "https://www.google.com/search"

# 1. Load Data
with open('books.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
books_list = data['categories']

with open('methods.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
methods_list = data['ai_study_framework']['methods']

# 2. Prompt Generation Logic
def generate_1000_prompts(books, methods):
    output = []
    for book in books:
        # Create a display string for the book
        book_display = f"{book['title']} by {book['author']}"
        for method in methods:
            # Replace placeholder with actual book info
            final_text = method['prompt'].replace("{title}", book_display)

            output.append({
                "book_title": book['title'],
                "method_type": method['name'],
                "generated_prompt": final_text  # This key must match the loop below
            })
    return output


html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Library Links</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            line-height: 1.6; 
            padding: 20px; /* Reduced from 40px for mobile screens */
            background-color: #f8f9fa; 
            margin: 0;
        }
        .container { 
            max-width: 900px; 
            margin: auto; 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .category-section { margin-bottom: 30px; }
        
        /* 2. BETTER READABILITY: Increased link size and tap area */
        .prompt-link { 
            display: block; 
            margin: 12px 0; 
            color: #1a0dab; 
            text-decoration: none; 
            font-size: 16px; /* 16px is the standard for mobile readability */
            padding: 5px 0; 
        }
        .prompt-link:hover { text-decoration: underline; background-color: #f1f3f4; }
        
        h1 { color: #202124; text-align: center; font-size: 1.5rem; }
        h2 { border-bottom: 2px solid #4285f4; color: #4285f4; padding-bottom: 5px; margin-top: 25px; font-size: 1.2rem; }
        .meta-info { font-size: 0.85em; color: #70757a; margin-right: 10px; font-weight: bold; }

        /* 3. OPTIONAL: Extra polish for very small screens */
        @media (max-width: 480px) {
            body { padding: 10px; }
            .container { padding: 15px; }
            h1 { font-size: 1.25rem; }
        }
    </style>
</head>
<body>
    <div class="container">
    <h1>Generated Research Links</h1>
"""

total_prompts_count = 0

# 4. Logic Execution
for category in books_list:
    html_content += f"<div class='category-section'>\n<h2>Category: {category['category']}</h2>\n"
    
    # Generate prompts for this specific category
    current_category_prompts = generate_1000_prompts(category['books'], methods_list)
    total_prompts_count += len(current_category_prompts)

    for item in current_category_prompts:
        if(item['method_type'] == 'The Big Picture Overview'):
          html_content += f"<div class='category-section'>\n<h3>Book: {item['book_title']}</h3>\n"
        # We use the key 'generated_prompt' defined in the function above
        actual_text = "propmt: "+item['generated_prompt']+" book: "+item['book_title']+" method: "+item['method_type']

        # URL Encoding for Google
        query_params = {
          'q': actual_text, 
          'udm': '50'  # <--- THIS FORCES AI MODE
        }
        encoded_query = urlencode(query_params)
        final_url = f"{base_url}?{encoded_query}"

        # HTML Escaping for the display text
        safe_prompt = html.escape(actual_text)
        method_label = html.escape(item['method_type']).upper()
        
        html_content += f'    <a class="prompt-link" href="{final_url}" target="_blank"><span class="meta-info">{method_label}</span></a>\n'

    html_content += "</div>\n"

html_content += """
    </div>
</body>
</html>
"""

# 5. Save Results
with open("prompts.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {total_prompts_count} prompts across all categories.")
