import json
import html
from urllib.parse import urlencode

# 1. Load Data
# tips.json should be a flat list of 100 strings
with open('tips.json', 'r', encoding='utf-8') as file:
    tips_data = json.load(file)
    # Handling both potential formats: {"fullstack_tips": [...]} or [...]
    tips_list = tips_data.get('fullstack_tips', tips_data)

# methods_to_explain.json should follow the ID/Name/Prompt structure we created
with open('methods_to_explain.json', 'r', encoding='utf-8') as file:
    methods_data = json.load(file)
    methods_list = methods_data.get('learning_methods', methods_data)

# 2. Prompt Generation Logic
def generate_study_prompts(tips, methods):
    output = []
    for index, tip in enumerate(tips):
        for method in methods:
            # Replace placeholder {tip} with the actual tip text
            final_text = method['prompt'].replace("{tip}", tip)
            output.append({
                "tip_id": index + 1,
                "tip_content": tip,
                "method_name": method['name'],
                "platform_type": method['platform_type'],
                "search_link": method['search_link'],
                "generated_prompt": final_text
            })
    return output

# 3. HTML & CSS
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Fullstack Mastery Dashboard</title>
    <style>
        html { scroll-behavior: smooth; }
        body { font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; padding: 20px; background-color: #f0f2f5; color: #1c1e21; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .index-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #4285f4; columns: 2; }
        .index-link { display: block; color: #1a73e8; text-decoration: none; margin: 5px 0; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .index-link:hover { color: #d93025; }
        .tip-section { margin-bottom: 40px; padding: 20px; border: 1px solid #e1e4e8; border-radius: 8px; transition: opacity 0.3s; }
        .tip-section.hidden { display: none; }
        h2 { color: #1a73e8; border-bottom: 2px solid #e8f0fe; padding-bottom: 10px; }
        .method-card { display: flex; align-items: center; justify-content: space-between; background: #fff; border: 1px solid #dee2e6; margin: 8px 0; padding: 12px; border-radius: 6px; text-decoration: none; color: inherit; transition: transform 0.1s; }
        .method-card:hover { transform: translateX(5px); background-color: #f1f3f4; }
        .method-card.visited { opacity: 0.5; border-left: 4px solid #34a853; }
        .meta { font-weight: bold; font-size: 0.75rem; color: #5f6368; text-transform: uppercase; }
        .prompt-text { font-size: 0.95rem; flex-grow: 1; margin: 0 15px; }
        .badge { padding: 2px 8px; border-radius: 12px; font-size: 10px; color: white; }
        .bg-youtube { background: #ff0000; } .bg-google_ai { background: #4285f4; } .bg-browser { background: #34a853; }
    </style>
</head>
<body>
    <div class="container">
    <h1>🚀 100 Steps to Fullstack Mastery</h1>
"""

# Generate Index
html_content += '<div class="index-section">'
for i, tip in enumerate(tips_list):
    safe_id = f"tip_{i+1}"
    html_content += f'<a class="index-link" href="#{safe_id}">{i+1}. {tip[:40]}...</a>'
html_content += '</div>'

# Generate Content
all_prompts = generate_study_prompts(tips_list, methods_list)

current_tip = None
for item in all_prompts:
    if current_tip != item['tip_id']:
        if current_tip is not None: html_content += "</div>"
        current_tip = item['tip_id']
        html_content += f"<div class='tip-section' id='tip_{current_tip}'><h2>{current_tip}. {item['tip_content']}</h2>"

    # Encoding for the URL
    query = urlencode({'q': item['generated_prompt']}) if item['platform_type'] != 'youtube' else urlencode({'search_query': item['generated_prompt']})
    final_url = f"{item['search_link']}{'&' if '?' in item['search_link'] else '?'}{query}"
    
    link_id = f"link_{item['tip_id']}_{item['method_name'].replace(' ', '_')}"
    
    html_content += f"""
        <a id="{link_id}" class="method-card" href="{final_url}" target="_blank" data-tip="{item['tip_id']}">
            <span class="meta">{item['method_name']}</span>
            <span class="prompt-text">{item['generated_prompt']}</span>
            <span class="badge bg-{item['platform_type']}">{item['platform_type']}</span>
        </a>
    """

html_content += """
    </div></div>
    <script>
        document.querySelectorAll('.method-card').forEach(card => {
            // Check localStorage on load
            if (localStorage.getItem(card.id)) card.classList.add('visited');

            card.addEventListener('click', function() {
                localStorage.setItem(this.id, 'true');
                this.classList.add('visited');
                
                // Optional: Check if all methods for this tip are done
                const tipId = this.dataset.tip;
                const siblings = document.querySelectorAll(`.method-card[data-tip="${tipId}"]`);
                const allDone = Array.from(siblings).every(s => localStorage.getItem(s.id));
                if (allDone) document.getElementById(`tip_${tipId}`).style.opacity = '0.3';
            });
        });
    </script>
</body></html>
"""

with open("fullstack_mastery.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Mastery Dashboard Generated: {len(all_prompts)} total study steps created.")
