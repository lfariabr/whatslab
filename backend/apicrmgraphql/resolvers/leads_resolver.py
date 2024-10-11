# lead resolver
# this is where we get the data

import requests
import re
import json
import time
import logging
from ..models import GraphQLClient
from ..token_manager import graphql_api_url, graphql_api_token
from backend.apicrmgraphql.dicts import dic_store_ident, dic_region_ident, stores, region_map

client = GraphQLClient(graphql_api_url, graphql_api_token)
logging.basicConfig(level=logging.DEBUG)

def query_leads(current_page, start_date, end_date, token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    payload = {
    'query': '''
    query LeadsQuery($filters: LeadFiltersInput, $pagination: PaginationInput) {
        fetchLeads(filters: $filters, pagination: $pagination) {
            data {
                createdAt
                id
                source {
                    title
                }
                store {
                    name
                }
                status {
                    label
                }
                customer {
                    id
                    name
                }
                name
                telephone
                email
            }
            meta {
                currentPage
                lastPage
            }
        }
    }
    ''',
    'variables': {
        'filters': {
            'createdAtRange': {
                'start': start_date,
                'end': end_date,
            },
        },
        'pagination': {
            'currentPage': current_page,
            'perPage': 200,  # Adjust as needed
        },
    },
}


    response = requests.post(
        graphql_api_url,
        headers=headers,
        data=json.dumps(payload)
    )

    # Log the raw response content
    logging.debug(f"Raw API response: {response.text}")

    try:
        result = response.json()
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        logging.error(f"Response content: {response.text}")
        raise

    if response.status_code == 200:
        if 'errors' in result:
            logging.error(f"GraphQL errors: {result['errors']}")
            raise Exception(f"GraphQL errors: {result['errors']}")
        else:
            return result
    else:
        logging.error(f"HTTP error {response.status_code}: {response.text}")
        response.raise_for_status()


def fetch_all_leads(start_date, end_date):
    current_page = 1
    all_leads = []
    token = graphql_api_token

    while True:
        try:
            data = query_leads(current_page, start_date, end_date, token)
            logging.debug(f"API response data (page {current_page}): {json.dumps(data, indent=2)}")

            if 'data' in data and 'fetchLeads' in data['data']:
                leads_data = data['data']['fetchLeads']['data']
                logging.debug(f"Leads data retrieved: {leads_data}")
                all_leads.extend(leads_data)

                meta = data['data']['fetchLeads']['meta']
                logging.info(f"Queried leads page: {current_page}/{meta['lastPage']} - startDate: {start_date} - endDate: {end_date}")

                if current_page >= meta['lastPage']:
                    break

                current_page += 1
                time.sleep(1)

            elif 'errors' in data:
                logging.error(f"GraphQL errors: {data['errors']}")
                break
            else:
                logging.error(f"Unexpected response structure: {data}")
                break

        except KeyError as e:
            logging.error(f"KeyError occurred: {e}")
            logging.error(f"Response content: {data}")
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(5)
            continue

    logging.debug(f"All leads collected: {all_leads}")
    return all_leads

def fetch_leads(start_date, end_date):
    return fetch_all_leads(start_date, end_date)

def filter_and_clean_leads(leads):
    # Regex patterns to filter leads
    # source_exclusive = r'Facebook Leads|Instagram Leads'
    store_exclusive = r'HOMA|PLÁSTICA|PRAIA GRANDE'

    # Exclude specific sources or stores
    leads_filtered = [
        lead for lead in leads
        # if 'source' in lead and not re.search(source_exclusive, lead['source'], re.IGNORECASE) 
        # and 'store' in lead and not re.search(store_exclusive, lead['store'], re.IGNORECASE)
        if 'store' in lead and 'name' in lead['store'] and not re.search(store_exclusive, lead['store']['name'], re.IGNORECASE)
    ]

    # Clean phone data
    for lead in leads_filtered:
        if 'phone' in lead:
            # Sanitizing the phone number by removing unwanted characters
            cleaned_phone = re.sub(r'\D', '', lead['phone'])
            lead['phone'] = cleaned_phone.strip()

        # Cleaning email, if needed
        if 'email' in lead:
            lead['email'] = lead['email'].strip()

        # Add any additional cleaning steps if needed

    return leads_filtered
    
    # return fetch_leads(start_date, end_date)

def create_lead(name, telephone, email, message, unidade, region):

    source_identifier = "662bf789-d04c-4ccf-8424-26b92595060c"

    region_identifier = dic_region_ident[region]
    store_identifier = dic_store_ident[unidade]

    telephone = str(telephone)

    query = """
    mutation ($data: CreateLeadInput!) {
        createLead(
            data: $data
        ) {
            email
            name
            message
            region {
                identifier
            }
            source {
                identifier
            }
            store {
                identifier
            }
            telephone
        }
    }
    """

    variables = {
        "data": {
            "email": email,
            "message": message,
            "name": name,
            "regionIdentifier": region_identifier,
            "sourceIdentifier": source_identifier,
            "storeIdentifier": store_identifier,
            "telephone": telephone
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {graphql_api_token}'
    }

    response = requests.post(graphql_api_url, json={'query': query, 'variables': variables}, headers=headers)
    response_data = response.json()

    if response.status_code == 200:
        print("Lead created successfully:", response_data)
    else:
        print("Failed to create lead:", response_data)

    return response_data