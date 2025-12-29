import ollama

def generate_blog_post(title, summary):
    # This prompt tells the model to use its internal knowledge 
    # to "expand" the news since it cannot browse the live web.
    prompt = f"""
    You are a professional tech blogger. 
    Write an engaging, SEO-friendly blog post description (approx 100 words).
    
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

# Example Usage
news_title = "The Best Tricks to Boost Your Bars: How to Fix Poor Reception on Your iPhone or Android"
news_summary = "iPhone: Carrier updates should just appear. Android: not all Android phones have carrier settings. Go to Settings > Network & internet > Internet. For both: Resetting network settings can help solve connectivity issues."

print("Generating Blog Description...")
print("-" * 30)
print(generate_blog_post(news_title, news_summary))