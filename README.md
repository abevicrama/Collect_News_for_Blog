# SUSL Auto Tech Blog

This project is an automated tech news aggregation and blogging platform. It scrapes tech news from various sources, categorizes them, generates blog posts, and serves them via a Django web application.

## Project Structure

- **`data_collect.py`**: Scrapes news articles from sources like CNN, Wired, TechCrunch, The Verge, etc.
- **`data_category.py`**: Categorizes the collected news articles using keywords (AI, Mobile, Computer, etc.).
- **`blog_details_generate.py`**: Generates full blog post content, including titles, bodies, and metadata.
- **`SUSL_Auto_Tech/`**: The Django web application directory.
    - **`load_posts.py`**: A management script to load the generated blog posts into the Django database.

## Workflow

### 1. Data Collection
Run the data collection script to fetch the latest news:
```bash
python data_collect.py
```
*Outputs to `collected_data/*.csv`*

### 2. Categorization
Categorize the collected raw data:
```bash
python data_category.py
```
*Outputs to `categorize_data/*.csv`*

### 3. Blog Post Generation
Generate formatted blog posts from the categorized data:
```bash
python blog_details_generate.py
```
*Outputs to `blog_post/blog_details.csv`*

### 4. Database Loading
Load the generated posts into the Django application:
```bash
cd SUSL_Auto_Tech
python load_posts.py
```

### 5. Running the Website
Start the Django development server:
```bash
cd SUSL_Auto_Tech
python manage.py runserver
```
Access the site at `http://127.0.0.1:8000/` (or your configured port).

## Features
- **Automated Content**: Pipeline to fetch and process news automatically.
- **Categorization**: Intelligent sorting of news into categories like AI, Mobile, Computer, etc.
- **Web Interface**: A Django-based frontend to view posts.
    - **Filtering**: View posts by category.
    - **Pagination**: Easy navigation through many posts.
    - **Contact Page**: Information to reach the developers.
    - **Responsive Design**: Modern UI with a dark theme.

## Requirements
- Python 3.10+
- Django 5.x
- Newspaper3k (for scraping)
- Pandas (for data manipulation)

## Setup
1. Install dependencies:
   ```bash
   pip install django newspaper3k pandas
   ```
2. Navigate to the Django project:
   ```bash
   cd SUSL_Auto_Tech
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

---
*Developed by Abeywickrama for*
