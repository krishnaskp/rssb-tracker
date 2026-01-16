import requests
import json
import os
from datetime import datetime

# 1. RSSB ka API URL jaha se data aata hai
API_URL = "https://rssb.rajasthan.gov.in/filterresult/0/0"

# 2. PDF ka Base URL (Jo file name ke aage lagega)
PDF_BASE_URL = "https://rssb.rajasthan.gov.in/storage/result_item/"

# Headers taki website ko lage hum browser hain
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}

def fetch_and_save_data():
    print("🔄 Connecting to RSSB Website...")
    
    try:
        # Website se data maang rahe hain (verify=False SSL error se bachne ke liye)
        response = requests.get(API_URL, headers=headers, verify=False)
        
        if response.status_code == 200:
            raw_data = response.json()
            
            # Data 'data' key ke andar hota hai
            items = raw_data.get('data', [])
            processed_list = []
            
            print(f"✅ Found {len(items)} items. Processing...")

            for item in items:
                # --- MAIN MAGIC ---
                # PDF ka link banana
                pdf_filename = item.get('result_link', '')
                full_pdf_link = PDF_BASE_URL + pdf_filename
                
                # Date format karna
                date_raw = item.get('created_at', '')
                try:
                    # Date convert: 2026-01-15T00... -> 15-01-2026
                    dt = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%d-%m-%Y')
                except:
                    formatted_date = date_raw

                # Naya data check karna (3 din purana)
                is_new_result = check_is_new(date_raw)

                # Saaf-suthra data object
                clean_item = {
                    "id": item.get('id'),
                    "exam": item.get('exam_name'),
                    "year": item.get('exam_year'),
                    "title": item.get('result'),
                    "link": full_pdf_link,   # Ye hai wo full link jo chahiye
                    "date": formatted_date,
                    "is_new": is_new_result
                }
                processed_list.append(clean_item)
            
            # File save karna (exam_data.json)
            with open('exam_data.json', 'w', encoding='utf-8') as f:
                json.dump(processed_list, f, ensure_ascii=False, indent=4)
                
            print("🎉 Done! 'exam_data.json' file created successfully.")
            
        else:
            print(f"❌ Error: Status Code {response.status_code}")
            
    except Exception as e:
        print(f"❌ Something went wrong: {e}")

def check_is_new(date_str):
    # Logic: Agar result 3 din ke andar ka hai to New hai
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        delta = datetime.now(dt.tzinfo) - dt
        return delta.days <= 3
    except:
        return False

if __name__ == "__main__":
    fetch_and_save_data()
