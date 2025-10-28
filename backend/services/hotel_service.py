import requests
import os
import time

HOTELS_API_KEY = os.getenv("HOTELS_API_KEY")

def get_destination_data(query):
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    headers = {
        "x-rapidapi-key": HOTELS_API_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }
    params = {"query": query}

    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()

    if not data.get("status") or not data.get("data"):
        raise Exception("No destination data found")

    top = data["data"][0]
    return {
        "name": top.get("name"),
        "dest_id": top.get("dest_id"),
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "nr_hotels": top.get("nr_hotels"),
    }


def search_hotels(city_name, start_date, end_date, adults):
    dest = get_destination_data(city_name)
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    headers = {
        "x-rapidapi-key": HOTELS_API_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    all_hotels, page_number, max_pages = [], 1, 5
    has_more_pages = True
    while has_more_pages and page_number <= max_pages:
        params = {
            "dest_id": dest["dest_id"],
            "search_type": "CITY",
            "adults": str(adults),
            "room_qty": "1",
            "page_number": str(page_number),
            "units": "metric",
            "languagecode": "en-us",
            "currency_code": "INR",
            "arrival_date": start_date,
            "departure_date": end_date,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors

            data = response.json()

            # Check the structure of the response
            if isinstance(data, dict) and "data" in data:
                if "hotels" in data["data"] and isinstance(data["data"]["hotels"], list):
                    current_page_hotels = data["data"]["hotels"]
                    all_hotels.extend(current_page_hotels)

                    # Check if there are more pages
                    if len(current_page_hotels) == 0:
                        has_more_pages = False
                        print(f"No more hotels found after page {page_number - 1}")
                    elif "meta" in data["data"]:
                        meta = data["data"]["meta"]
                        if isinstance(meta, dict) and "page_number" in meta and "total_pages" in meta:
                            current_page = int(meta["page_number"])
                            total_pages = int(meta["total_pages"])
                            print(f"Page {current_page} of {total_pages}")

                            if current_page >= total_pages:
                                has_more_pages = False
                                print("Reached the last page")
                        else:
                            # If we can't determine total pages but got results, try the next page
                            print(f"Got {len(current_page_hotels)} hotels on page {page_number}")
                else:
                    print("No hotels data found in the response")
                    has_more_pages = False
            else:
                print("Unexpected response format")
                has_more_pages = False

            page_number += 1

            # Add a delay to avoid rate limiting
            time.sleep(1.5)

        except Exception as e:
            print(f"Error fetching page {page_number}: {str(e)}")
            break

    print(f"Total hotels collected: {len(all_hotels)}")
    return {
        "total_hotels": len(all_hotels),
        "hotels": all_hotels
    }

def parse_hotel_info(city_name, start_date, end_date, adults):
    hotels_data = search_hotels(city_name, start_date, end_date, adults)
    results = []
    for hotel in hotels_data["hotels"]:
        prop = hotel["property"]
        price_info = prop["priceBreakdown"]
        total = round(price_info["grossPrice"]["value"] + price_info["excludedPrice"]["value"])
        info = {
            "name": prop["name"],
            "rating": f'{prop.get("accuratePropertyClass", "N/A")} out of 5',
            "review_score": f'{prop.get("reviewScore", "N/A")} ({prop.get("reviewScoreWord", "")})',
            "review_count": prop.get("reviewCount", "N/A"),
            "checkin": prop["checkin"],
            "checkout": prop["checkout"],
            "price(incl_taxes)": total,
            "free_cancellation": "YES" if "Free cancellation" in hotel["accessibilityLabel"] else "NO",
            "no_prepayment": "YES" if "No prepayment" in hotel["accessibilityLabel"] else "NO",
            "photo": prop["photoUrls"][0] if prop.get("photoUrls") else "No image",
            "longitude": prop.get("longitude", "N/A"),
            "latitude": prop.get("latitude", "N/A")
        }
        results.append(info)
    return results
