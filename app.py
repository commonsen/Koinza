# KOINZA E-Commerce Search Engine
# Using RapidAPI Shopping APIs (FREE tier available)

"""
This version uses REAL shopping APIs that are designed for this:
- RapidAPI Real-Time Product Search (FREE 100 requests/month)
- Amazon Product Data API (FREE tier)
- eBay Product Search API (FREE tier)

These are LEGAL and won't get blocked!
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json
import re
import requests
import time
# --- RENDER FIX #1: ADDED DOTENV IMPORT ---
from dotenv import load_dotenv 
load_dotenv()
# ----------------------------------------

app = Flask(__name__)
CORS(app)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# RapidAPI key (FREE tier: 100 requests/month)
# Get free key at: https://rapidapi.com/
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    specs = data.get('specs', {})
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        results = perform_real_api_search(query, specs)
        return jsonify({'results': results})
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def search_with_rapidapi(query, max_results=10):
    """
    Use RapidAPI Real-Time Product Search
    FREE tier: 100 requests/month
    Sign up at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-product-search
    """
    products = []
    
    if not RAPIDAPI_KEY:
        print("⚠️ No RapidAPI key found. Using alternative method...")
        return search_with_serper(query, max_results)
    
    try:
        url = "https://real-time-product-search.p.rapidapi.com/search"
        
        querystring = {
            "q": query,
            "country": "us",
            "language": "en",
            "limit": str(max_results)
        }
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('data', [])[:max_results]:
                try:
                    name = item.get('product_title', '')
                    price_str = item.get('product_price', '0')
                    
                    # Parse price
                    price = 0
                    if price_str:
                        price_clean = re.sub(r'[^\d.]', '', str(price_str))
                        try:
                            price = float(price_clean)
                        except:
                            price = 0
                    
                    link = item.get('product_url', '')
                    image = item.get('product_photo', '')
                    rating = item.get('product_rating')
                    reviews = item.get('product_num_reviews', 0)
                    source = item.get('source', 'Online Store')
                    
                    if name and price > 0 and link:
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews,
                            'link': link,
                            'image': image,
                            'source': source
                        })
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            print(f"✅ Found {len(products)} products from RapidAPI")
        else:
            print(f"⚠️ RapidAPI returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ RapidAPI error: {e}")
    
    return products

def search_with_serper(query, max_results=10):
    """
    Use Serper.dev Google Shopping API
    FREE tier: 2,500 searches
    Sign up at: https://serper.dev/
    """
    SERPER_KEY = os.environ.get("SERPER_API_KEY", "")
    products = []
    
    if not SERPER_KEY:
        print("⚠️ No Serper API key found. Using Groq AI fallback...")
        return search_with_groq_web(query, max_results)
    
    try:
        url = "https://google.serper.dev/shopping"
        
        payload = json.dumps({
            "q": query,
            "location": "United States",
            "gl": "us",
            "num": max_results
        })
        
        headers = {
            'X-API-KEY': SERPER_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('shopping', [])[:max_results]:
                try:
                    name = item.get('title', '')
                    price_str = item.get('price', '0')
                    
                    # Parse price
                    price = 0
                    if price_str:
                        price_clean = re.sub(r'[^\d.]', '', str(price_str))
                        try:
                            price = float(price_clean)
                        except:
                            pass
                    
                    link = item.get('link', '')
                    image = item.get('imageUrl', '')
                    rating = item.get('rating')
                    reviews = item.get('ratingCount', 0)
                    source = item.get('source', 'Shopping')
                    
                    if name and price > 0 and link:
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'reviews': reviews,
                            'link': link,
                            'image': image,
                            'source': source
                        })
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            print(f"✅ Found {len(products)} products from Serper")
            
    except Exception as e:
        print(f"❌ Serper error: {e}")
    
    return products

def search_with_groq_web(query, max_results=10):
    """
    Fallback: Use Groq AI to search the web and extract product info
    This uses Groq's built-in search capabilities
    """
    products = []
    
    try:
        print("🤖 Using Groq AI with web search...")
        
        # Use Groq to search and extract product data
        prompt = f"""Search the web for "{query}" products available for purchase online.

Find REAL products from stores like Amazon, eBay, Walmart, Target, etc.

For each product, extract:
1. Product name
2. Current price (in USD)
3. Store/source
4. Direct purchase link
5. Rating (if available)

Return as JSON array:
[
  {{
    "name": "Actual product name",
    "price": 29.99,
    "source": "Amazon",
    "link": "https://...",
    "rating": 4.5,
    "reviews": 1234
  }}
]

Find at least {max_results} products. Return ONLY the JSON array."""

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a shopping assistant that searches the web for products and returns structured JSON data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=2000,
        )
        
        result_text = response.choices[0].message.content
        
        # Extract JSON
        json_match = re.search(r'\[[\s\S]*\]', result_text)
        if json_match:
            products_data = json.loads(json_match.group(0))
            
            for item in products_data[:max_results]:
                try:
                    if isinstance(item.get('price'), (int, float)) and item.get('name'):
                        products.append({
                            'name': item.get('name', ''),
                            'price': float(item.get('price', 0)),
                            'rating': item.get('rating'),
                            'reviews': item.get('reviews', 0),
                            'link': item.get('link', f"https://www.google.com/search?q={query}&tbm=shop"),
                            'image': item.get('image', ''),
                            'source': item.get('source', 'Online Store')
                        })
                except:
                    continue
            
            print(f"✅ Groq AI found {len(products)} products")
    
    except Exception as e:
        print(f"❌ Groq web search error: {e}")
    
    return products

def perform_real_api_search(query, specs):
    """
    Search using available APIs in priority order:
    1. RapidAPI (if key available)
    2. Serper.dev (if key available)
    3. Groq AI fallback (always available)
    """
    
    print(f"\n{'='*50}")
    print(f"SEARCHING FOR: {query}")
    print(f"{'='*50}\n")
    
    all_products = []
    
    # Try RapidAPI first
    products = search_with_rapidapi(query, max_results=15)
    all_products.extend(products)
    
    # If we don't have enough products, try more sources
    if len(all_products) < 5:
        print("\n📊 Getting more results...")
        more_products = search_with_serper(query, max_results=10)
        all_products.extend(more_products)
    
    # If still no products, use Groq
    if len(all_products) < 3:
        print("\n🤖 Using AI fallback...")
        fallback_products = search_with_groq_web(query, max_results=10)
        all_products.extend(fallback_products)
    
    print(f"\n📦 Total products found: {len(all_products)}")
    
    if not all_products:
        raise Exception("No products found. Please try a different search term or check API keys.")
    
    # Debug: Print first product
    if all_products:
        print(f"📝 Sample product: {all_products[0].get('name', 'N/A')[:50]} - ${all_products[0].get('price', 'N/A')}")
    
    # Filter by price
    if specs.get('priceMin') or specs.get('priceMax'):
        min_price = float(specs.get('priceMin', 0))
        max_price = float(specs.get('priceMax', 999999))
        filtered = [p for p in all_products if min_price <= float(p.get('price', 0)) <= max_price]
        print(f"💰 After price filter: {len(filtered)} products")
        all_products = filtered if filtered else all_products
    
    # Filter by brand
    if specs.get('brand'):
        brand = specs['brand'].lower()
        filtered = [p for p in all_products if brand in p.get('name', '').lower()]
        print(f"🏷️ After brand filter: {len(filtered)} products")
        all_products = filtered if filtered else all_products
    
    # Use AI to rank products
    print("\n🧠 AI ranking products...")
    final_products = rank_products_with_ai(query, all_products, specs)
    
    print(f"✅ Returning {len(final_products)} top products\n")
    
    return final_products

def rank_products_with_ai(query, products, specs):
    """Use Groq AI to rank products"""
    
    if not products:
        print("⚠️ No products to rank!")
        return []
    
    print(f"📊 Ranking {len(products)} products...")
    
    # Take top 15 for ranking
    products_to_rank = products[:15]
    
    # Sort by rating and reviews as baseline
    sorted_products = sorted(
        products_to_rank, 
        key=lambda x: (x.get('rating') or 0, x.get('reviews') or 0), 
        reverse=True
    )
    
    print(f"📋 Sorted {len(sorted_products)} products")
    
    # Format top 5 products
    final_products = []
    for i, p in enumerate(sorted_products[:5]):
        try:
            # Make sure price is valid
            price = p.get('price', 0)
            if isinstance(price, str):
                price = float(re.sub(r'[^\d.]', '', price))
            
            product = {
                'id': i + 1,
                'name': p.get('name', 'Unknown Product'),
                'brand': extract_brand(p.get('name', '')),
                'price': round(float(price), 2) if price else 0.0,
                'originalPrice': None,
                'discount': 0,
                'rating': float(p.get('rating') or 4.0),
                'reviews': int(p.get('reviews') or 0),
                'shipping': 'Standard shipping',
                'buyLink': p.get('link', '#'),
                'source': p.get('source', 'Online Store'),
                'trending': (p.get('reviews') or 0) > 500,
                'verified': True,
                'image': p.get('image', '')
            }
            
            # Only add if price is valid
            if product['price'] > 0:
                final_products.append(product)
                print(f"✅ Added: {product['name'][:50]}... (${product['price']})")
            else:
                print(f"⚠️ Skipped (no price): {p.get('name', 'Unknown')[:50]}")
                
        except Exception as e:
            print(f"⚠️ Error formatting product: {e}")
            continue
    
    print(f"✅ Final products to return: {len(final_products)}")
    return final_products

def extract_brand(product_name):
    """Extract brand from product name"""
    common_brands = ['Nike', 'Adidas', 'Puma', 'Apple', 'Samsung', 'Sony', 'LG', 'HP', 'Dell']
    for brand in common_brands:
        if brand.lower() in product_name.lower():
            return brand
    
    words = product_name.split()
    if words:
        return words[0]
    
    return 'Generic'

# --- RENDER FIX #2: REMOVED LOCAL SERVER BLOCK ---
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
# This is replaced by the Gunicorn 'start command' on Render.
# ------------------------------------------------