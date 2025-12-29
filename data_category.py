import pandas as pd
import os
import glob
import re

def categorize_summary(text):
    if not isinstance(text, str):
        return 'Other'
    
    text = text.lower()
    
    def contains_keyword(text, keywords):
        for k in keywords:
            # Use regex for word boundary for all keywords to avoid substring false positives
            # e.g. 'intel' should not match 'intelligence'
            pattern = r'\b' + re.escape(k) + r'\b'
            if re.search(pattern, text):
                return True
        return False

    if contains_keyword(text, ['computer', 'laptop', 'desktop', 'pc', 'mac', 'windows', 'processor', 'nvidia', 'amd', 'intel']):
        return 'Computer'
    elif contains_keyword(text, ['mobile', 'phone', 'app', 'android', 'ios', 'smartphone', 'iphone', 'samsung', 'pixel', '5g']):
        return 'Mobile'
    elif contains_keyword(text, ['ai', 'artificial intelligence', 'machine learning', 'llm', 'chatgpt', 'neural', 'gemini', 'copilot', 'robot']):
        return 'AI'
    elif contains_keyword(text, ['gadget', 'wearable', 'watch', 'smart', 'device', 'headset', 'vr', 'ar', 'camera']):
        return 'Tech Gadgets'
    elif contains_keyword(text, ['science','technology','technical','scientific','automate','iot','crypto','blockchain',]):
        return 'Other'
    else:
        return 'Nothing'

def load_and_process_data():
    data_dir = 'collected_data'
    output_dir = 'categorize_data'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
        
    all_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not all_files:
        print("No CSV files found in collected_data/")
        return

    df_list = []
    
    # Define expected columns
    columns = ["article_url", "article_title", "article_summary", "publish_date", "article_authors", "timestamp","checked"]
    
    for filename in all_files:
        try:
            # Read new collected data
            # Read with no header, then assign names manually
            df_new = pd.read_csv(filename, header=None, names=columns, on_bad_lines='skip')
            
            if df_new.empty:
                continue
                
            # Filter out header rows if present
            if 'article_url' in df_new.columns:
                 df_new = df_new[df_new['article_url'] != 'article_url']
            
            # Determine output path
            basename = os.path.basename(filename)
            output_path = os.path.join(output_dir, basename)
            
            # Check if output file already exists to preserve state
            if os.path.exists(output_path):
                # Read existing data
                try:
                    df_existing = pd.read_csv(output_path)
                    existing_urls = set(df_existing['article_url'].astype(str))
                    print(f"Loaded {len(df_existing)} existing rows from {output_path}")
                except Exception as ex:
                    print(f"Error reading existing file {output_path}: {ex}. Overwriting.")
                    df_existing = pd.DataFrame()
                    existing_urls = set()
            else:
                df_existing = pd.DataFrame()
                existing_urls = set()

            # Filter new data that is NOT in existing
            # Ensure proper string comparison for URLs
            if not df_new.empty:
                 df_new = df_new[~df_new['article_url'].astype(str).isin(existing_urls)]
            
            if df_new.empty:
                print(f"No new articles for {basename}")
                if not df_existing.empty:
                     df_list.append(df_existing) # Add existing to stats
                continue

            print(f"Processing {len(df_new)} new articles for {basename}")

            # Ensure summary is string
            if 'article_summary' in df_new.columns:
                df_new['article_summary'] = df_new['article_summary'].astype(str)
                # Apply categorization
                df_new['Category'] = df_new['article_summary'].apply(categorize_summary)
                df_new['checked'] = False
            else:
                df_new['Category'] = 'Other' # Default if column missing
                df_new['checked'] = False

            # Combine existing and new
            if not df_existing.empty:
                df_final = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_final = df_new
            
            # Save properly with header, index=False
            df_final.to_csv(output_path, index=False)
            print(f"Saved/Updated categorized data to {output_path} ({len(df_final)} rows)")
            
            # Add to list for aggregate stats
            df_list.append(df_final)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if not df_list:
        print("No valid data processed.")
        return

    combined_df = pd.concat(df_list, ignore_index=True)

    print("\n--- Overall Category Distribution ---")
    if 'Category' in combined_df.columns:
        print(combined_df['Category'].value_counts())
    
    print("\n--- Sample Results ---")
    if 'article_title' in combined_df.columns:
        combined_df['article_title_short'] = combined_df['article_title'].str[:50]
        print(combined_df[['article_title_short', 'Category']].head(10).to_string(index=False))

if __name__ == "__main__":
    load_and_process_data()
