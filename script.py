
import requests
from openai import OpenAI
import json

SCRAPING_TASK_UID = "your_browserbear_task_id"
BROWSERBEAR_API_KEY = "your_browserbear_api_key"
BROWERBEAR_RESULT_UID = "your_browserbear_task_result_id"
OPENAI_API_KEY = "your_openai_api_key"

client = OpenAI(api_key=OPENAI_API_KEY)

def scrape_data(target_url, job_type, fields_array):
    url = f"https://api.browserbear.com/v1/tasks/{SCRAPING_TASK_UID}/runs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BROWSERBEAR_API_KEY}",
    }
    
    search_fields = ""
    for i, field in enumerate(fields_array):
        search_fields += f"{field}\n" if i != len(fields_array)-1 else field

    print(search_fields)
    
    data = {
        "steps": [
            {
                "uid": "1RNV0rb0dQwbOxmQ6X",
                "action": "go",
                "config": {
                    "url": target_url,
                    "waitUntil": "networkidle"
                }
            },
            {
                "uid": "qL25wVyl6gdzE4mJ1x",
                "action": "ai_save_links",
                "config": {
                    "type": job_type
                }
            },
            {
                "uid": "lYXA8Kz19QDzLV94N7",
                "action": "ai_save_data",
                "config": {
                "labels": search_fields
                },
                "iterate": True # loop over the previous step's links
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    print(f"Scraping {fields_array} from {target_url}...")
    
    return response.json()

def get_scraped_data(result_uid):

    job_status = "running"
    result = ""

    get_url = f"https://api.browserbear.com/v1/tasks/{SCRAPING_TASK_UID}/runs/{result_uid}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BROWSERBEAR_API_KEY}",
    }
    
    while job_status == "running":
        response = requests.get(get_url, headers=headers)
        result = response.json()
        job_status = result["status"]

    return result["outputs"][BROWERBEAR_RESULT_UID]

scraping_task = scrape_data("https://playground.browserbear.com/jobs/", "jobs", ["job_title", "company", "salary", "location"], ) # scraping jobs
# scraping_task = scrape_data("https://playground.browserbear.com/products/", "produtcs", ["title", "price", "rating"]) # scraping products
# scraping_task = scrape_data("https://www.browserbear.com/blog/", "articles", ["title", "author", "description"]) # scraping articles

data = get_scraped_data(scraping_task["uid"])
print(data)

# Set up the initial system message
system_message = {"role": "system",
                  "content": "You are a helpful assistant that analyzes information. Analyze this data and answer my questions based on the data:" + json.dumps(data)}

# Start the conversation with the system message
conversation = [system_message]

# Add user message to the conversation
user_message = {"role": "user", "content": "How many jobs are there? What are the jobs with the top 5 highest salary? What is the avarage salary?"}
conversation.append(user_message)

# Pass data to ChatGPT and get the response
response = client.chat.completions.create(model="gpt-4-1106-preview", messages=conversation)

# Extract and print the assistant's reply
assistant_reply = response.choices[0].message.content
print(f"Assistant: {assistant_reply}")


    
