import ollama
import csv
import os
import glob
import uuid

def generate_blog_post(title, summary):
    # This prompt tells the model to use its internal knowledge 
    # to "expand" the news since it cannot browse the live web.
    prompt = f"""
    You are a professional tech blogger. 
    Write an engaging, SEO-friendly blog post description (approx 150 words).
    include only description without title and fomattings

    TITLE: {title}
    SUMMARY: {summary}
    
    INSTRUCTION: Write a catchy opening, explain the technical importance, 
    and end with a call to action. Add a few more relevant tech details 
    that a reader would find helpful.
    """

    response = ollama.chat(model='llama3.2:1b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    return response['message']['content']

def save_to_file():
    input_dir = 'categorize_data'
    output_dir = 'blog_post'
    details_csv_path = os.path.join(output_dir, "blog_details.csv")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not all_files:
        print("No CSV files found in categorize_data/")
        return
    
    for filename in all_files:
        print(f"Processing {filename}...")
        rows = []
        fieldnames = []
        updated = False
        
        # Read all rows first
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        # Process rows
        for row in rows:
            # Check 'checked' status. Handle strings 'False', 'True', boolean, or missing
            # If 'checked' column is missing, treat as False (new) to be safe, or True? 
            # Original plan said default True, but if column missing in old data, we might want to process it?
            # data_category.py sets it to False now.
            checked_val = row.get('checked', 'False') 
            
            if str(checked_val).lower() == 'false':
                
                title = row.get('article_title', 'Untitled')
                summary = row.get('article_summary', '')
                category = row.get('Category', 'Other')
                author = row.get('article_authors', '')
                url = row.get('article_url', '')
                publish_date = row.get('publish_date', '')
                
                post_id = str(uuid.uuid4())
                category_dir = os.path.join(output_dir, category)
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                
                print(f"Generating for: {title[:30]}...")
                try:
                    content = generate_blog_post(title, summary)
                    
                    # Save content validation
                    if content:
                        # Save content to txt
                        with open(os.path.join(category_dir, f"{post_id}.txt"), 'w', encoding='utf-8') as output_file:
                            output_file.write(content)
                        
                        # Update blog_details.csv
                        file_exists = os.path.isfile(details_csv_path) and os.path.getsize(details_csv_path) > 0
                        
                        with open(details_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            if not file_exists:
                                writer.writerow(["post_id", "title", "content", "category", "author", "url", "publish_date", "publish", "checked"])
                            
                            writer.writerow([post_id, title, content, category, author, url, publish_date, False, True])
                        
                        # Mark as checked in memory
                        row['checked'] = True
                        updated = True
                    else:
                         print(f"Failed to generate content for {title}")

                except Exception as e:
                    print(f"Error generating/saving post: {e}")
            else:
                pass # Already checked

        # Write back to source file if updated
        if updated and fieldnames:
             try:
                # Ensure 'checked' is in fieldnames if it wasn't
                if 'checked' not in fieldnames:
                    fieldnames.append('checked')
                    
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                print(f"Updated {filename} with new checked status.")
             except Exception as e:
                 print(f"Error updating source file {filename}: {e}")

save_to_file()