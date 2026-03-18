import json
import html
from urllib.parse import urlencode

# 1. Load Data (Assuming files exist)
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
        book_display = f"{book['title']} by {book['author']}"
        for method in methods:
            final_text = method['prompt'].replace("{title}", book_display)
            output.append({
                "author": book['author'],
                "book_title": book['title'],
                "method_type": method['name'],
                "platform_type": method['platform_type'],
                "search_link": method['search_link'],
                "generated_prompt": final_text
            })
    return output

# 3. HTML Header & CSS (Added smooth scrolling)
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Library Links</title>
    <style>
        html { scroll-behavior: smooth; } /* Makes the jump look nice */
        body { font-family: -apple-system, sans-serif; line-height: 1.6; padding: 20px; background-color: #f8f9fa; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .index-section { background: #e8f0fe; padding: 15px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #4285f4; }
        .index-link { display: block; color: #1a0dab; text-decoration: none; margin: 4px 0; font-size: 14px; }
        .index-link:hover { text-decoration: underline; }
        .category-section { margin-bottom: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .prompt-link { display: block; margin: 12px 0; color: #1a0dab; text-decoration: none; font-size: 16px; padding: 5px 0; }
        .prompt-link.visited { display: none; }
        .book-section.hidden { display: none; }
        h1 { text-align: center; }
        h2 { color: #4285f4; border-bottom: 2px solid #4285f4; }
        h3 { background: #f1f3f4; padding: 10px; border-radius: 4px; }
        .meta-info { font-size: 0.85em; color: #70757a; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
    <h1>Generated Research Links</h1>
"""

# --- NEW: GENERATE THE INDEX (TABLE OF CONTENTS) ---
html_content += '<div class="index-section"><h2>Quick Index</h2>'
for category in books_list:
    for book in category['books']:
        # Create a URL-safe ID by replacing spaces with underscores
        book_id = f"book_{book['title'].replace(' ', '_')}"
        html_content += f'<a class="index-link" href="#{book_id}">{book["title"]} by {book["author"]}</a>'
html_content += '</div>'
# ----------------------------------------------------

total_prompts_count = 0

# 4. Logic Execution
for category in books_list:
    html_content += f"<div class='category-section'>\n<h2>Category: {category['category']}</h2>\n"
    
    current_category_prompts = generate_1000_prompts(category['books'], methods_list)
    total_prompts_count += len(current_category_prompts)

    # Track the first method for each book to add the heading
    book_headings_added = set()
    for item in current_category_prompts:
        # Create the same ID used in the Index
        book_id = f"book_{item['book_title'].replace(' ', '_')}"
        
        # Add heading only once per book
        if book_id not in book_headings_added:
            html_content += f"<div class='book-section' id='{book_id}'>\n"
            html_content += f"<h3>Book: {item['book_title']} by {item['author']}</h3>\n"
            book_headings_added.add(book_id)

        actual_text = f"prompt: {item['generated_prompt']} and the book is: {item['book_title']} and the method is: {item['method_type']}"


        # 1. Define the search prompt text
        # Note: We include the book title and author to ensure the AI has full context
        actual_text = f"Act as an expert book analyst. {item['generated_prompt']} (Book: {item['book_title']} by {item['author']})"

        # 2. Get platform-specific details from the method
        # Default to standard Google if keys are missing
        method_base_url = item.get('search_link', "https://www.google.com/search?q=")
        platform = item.get('platform_type', 'google_web')

        # 3. Dynamic URL Encoding based on Platform
        if platform == 'youtube':
            # YouTube uses 'search_query' as the parameter
            query_params = {'search_query': actual_text}
            final_url = f"{method_base_url}{urlencode(query_params)}"

        elif platform == 'goodreads':
            # For Goodreads, searching by Book Title + Author is most effective
            query_params = {'q': f"{item['book_title']} {item['author']}"}
            final_url = f"{method_base_url}{urlencode(query_params)}"

        elif platform == 'google_ai':
            query_params = {'q': actual_text}
            final_url = f"{method_base_url}&{urlencode(query_params)}"

        else:
            # Standard Google search (google_web)
            query_params = {'q': actual_text}
            final_url = f"{method_base_url}{urlencode(query_params)}"

        # 4. (Optional) Assign a CSS class for styling the link based on platform
        platform_css = f"btn-{platform}"

        # Create a unique ID for each link
        link_id = f"link_{item['book_title'].replace(' ', '_')}_{item['method_type'].replace(' ', '_')}"
        method_label = html.escape(item['method_type']).upper()
        html_content += f'    <a id="{link_id}" class="prompt-link" href="{final_url}" target="_blank" data-book="{item["book_title"]}" data-method="{item["method_type"]}"><span class="meta-info">{method_label}</span></a>\n'
    
    # Close book-section divs
    for _ in book_headings_added:
        html_content += "</div>\n"

    html_content += "</div>\n"

html_content += """</div>
<script>
    // Function to mark a link as visited
    function markLinkAsVisited(linkId, bookTitle) {
        // Save to localStorage
        localStorage.setItem(linkId, 'visited');
        
        // Hide the clicked link
        const linkElement = document.getElementById(linkId);
        if (linkElement) {
            linkElement.classList.add('visited');
        }
        
        // Check if all links for this book are visited
        checkBookCompletion(bookTitle);
    }

    // Function to check if all links for a book are visited
    function checkBookCompletion(bookTitle) {
        // Find all links for this book
        const allLinks = document.querySelectorAll(`.prompt-link[data-book="${bookTitle}"]`);
        let allVisited = true;
        
        allLinks.forEach(link => {
            const linkId = link.id;
            if (localStorage.getItem(linkId) !== 'visited') {
                allVisited = false;
            }
        });
        
        if (allVisited) {
            // Find the book section to hide
            // The book section is the parent div with class 'book-section' that contains the h3 with the book title
            // Since we structured it with a div wrapping each book, we can find it by id
            const bookId = 'book_' + bookTitle.replace(/ /g, '_');
            const bookSection = document.getElementById(bookId);
            if (bookSection) {
                bookSection.classList.add('hidden');
            }
        }
    }

    // On page load, hide visited links and check book completion
    document.addEventListener('DOMContentLoaded', function() {
        // Hide individual visited links
        const allLinks = document.querySelectorAll('.prompt-link');
        allLinks.forEach(link => {
            const linkId = link.id;
            if (localStorage.getItem(linkId) === 'visited') {
                link.classList.add('visited');
            }
        });
        
        // For each unique book, check if all its links are visited
        const uniqueBooks = new Set();
        allLinks.forEach(link => {
            uniqueBooks.add(link.getAttribute('data-book'));
        });
        
        uniqueBooks.forEach(bookTitle => {
            if (bookTitle) {
                checkBookCompletion(bookTitle);
            }
        });
        
        // Add click event listeners to all links
        allLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Allow the link to open in a new tab
                // We'll mark it as visited after a short delay to ensure the click is processed
                setTimeout(() => {
                    const linkId = this.id;
                    const bookTitle = this.getAttribute('data-book');
                    markLinkAsVisited(linkId, bookTitle);
                }, 100);
            });
        });
    });
</script>
</body></html>
"""

# 5. Save Results
with open("prompts.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {total_prompts_count} prompts with a Quick Index.")
