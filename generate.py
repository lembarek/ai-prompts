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
        .book-section.hidden { display: none; }
        .book-section.filter-hidden { display: none; }
        h1 { text-align: center; }
        h2 { color: #4285f4; border-bottom: 2px solid #4285f4; }
        h3 { background: #f1f3f4; padding: 10px; border-radius: 4px; }
        .meta-info { font-size: 0.85em; color: #70757a; font-weight: bold; }
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        .filter-btn {
            padding: 10px 20px;
            border: 2px solid #4285f4;
            background-color: white;
            color: #4285f4;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .filter-btn:hover {
            background-color: #e8f0fe;
        }
        .filter-btn.active {
            background-color: #4285f4;
            color: white;
        }
        .prompt-link.filter-hidden {
            display: none;
        }
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

# Add filter buttons
html_content += '''
<div class="filter-buttons">
    <button class="filter-btn active" data-filter="all">Show All Links</button>
    <button class="filter-btn" data-filter="saved">Show Saved Links Only</button>
    <button class="filter-btn" data-filter="unsaved">Show Unsaved Links Only</button>
</div>
'''

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
        if len(book_headings_added) and book_id not in book_headings_added:
            html_content += f"</div>\n"

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
        method_base_url = item.get('search_link', "https://www.google.com/search?")
        platform = item.get('platform_type', 'google_web')

        # 3. Dynamic URL Encoding based on Platform
        if platform == 'youtube':
            # YouTube uses 'search_query' as the parameter
            actual_text = f"{item['generated_prompt']} (Book: {item['book_title']} by {item['author']})"
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

    html_content += f"</div>\n"

    # Close book-section divs
    # for book_id in book_headings_added:
        # html_content += "</div>\n"

    html_content += "</div>\n"

html_content += """</div>
<script>
    // Function to mark a link as visited
    function markLinkAsVisited(linkId, bookTitle) {
        // Save to localStorage
        localStorage.setItem(linkId, 'visited');
        
        // Don't add 'visited' class to hide the link
        // Instead, reapply the current filter which will handle visibility
        // Check if all links for this book are visited
        checkBookCompletion(bookTitle);
        // Reapply current filter after marking as visited
        applyCurrentFilter();
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

        const bookId = 'book_' + bookTitle.replace(/ /g, '_');
        const bookSection = document.getElementById(bookId);
        if (bookSection) {
            if (allVisited) {
                bookSection.classList.add('hidden');
            } else {
                // If not all visited, remove the hidden class
                bookSection.classList.remove('hidden');
            }
        }
    }

    // Filter functions
    function applyFilter(filterType) {
        const allLinks = document.querySelectorAll('.prompt-link');
        // First, reset all links and book sections
        allLinks.forEach(link => {
            link.classList.remove('filter-hidden');
        });
        // Reset book sections to be visible (except those where all links are visited)
        document.querySelectorAll('.book-section').forEach(section => {
            section.classList.remove('filter-hidden');
        });
        
        // Apply link filtering
        allLinks.forEach(link => {
            const linkId = link.id;
            const isVisited = localStorage.getItem(linkId) === 'visited';
            
            if (filterType === 'saved') {
                if (!isVisited) {
                    link.classList.add('filter-hidden');
                }
            } else if (filterType === 'unsaved') {
                if (isVisited) {
                    link.classList.add('filter-hidden');
                }
            }
            // 'all' filter: do nothing, all links are visible
        });
        
        // Now, for each book section, check if it has any visible links
        // If not, hide the entire book section
        document.querySelectorAll('.book-section').forEach(section => {
            const bookId = section.id;
            // Find all links within this book section
            const linksInSection = section.querySelectorAll('.prompt-link');
            let hasVisibleLink = false;
            linksInSection.forEach(link => {
                if (!link.classList.contains('filter-hidden')) {
                    hasVisibleLink = true;
                }
            });
            // If no visible links, hide the book section
            if (!hasVisibleLink) {
                section.classList.add('filter-hidden');
            }
        });
        
        // Update button active states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-filter') === filterType) {
                btn.classList.add('active');
            }
        });
    }
    
    function applyCurrentFilter() {
        const activeBtn = document.querySelector('.filter-btn.active');
        if (activeBtn) {
            const filterType = activeBtn.getAttribute('data-filter');
            applyFilter(filterType);
        }
    }

    // On page load, check book completion and apply filter
    document.addEventListener('DOMContentLoaded', function() {
        // Don't add 'visited' class to hide links
        // Instead, we'll rely on the filter to show/hide them
        
        // For each unique book, check if all its links are visited
        const allLinks = document.querySelectorAll('.prompt-link');
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
        
        // Add event listeners to filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const filterType = this.getAttribute('data-filter');
                applyFilter(filterType);
            });
        });
        
        // Apply the default filter (all)
        applyFilter('all');
    });
</script>
</body></html>
"""

# 5. Save Results
with open("prompts.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {total_prompts_count} prompts with a Quick Index.")
