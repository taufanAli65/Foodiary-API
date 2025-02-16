# Foodiary API

This API allows you to search for food items and retrieve their nutritional information using the FatSecret API.

## Setup

1. Clone the repository.
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file in the root directory and add your FatSecret API credentials:
    ```
    CLIENT_ID=your_client_id
    CLIENT_SECRET=your_client_secret
    ```

## Running the API

To run the API, use the following command:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Endpoints

### Search Food

- **URL:** `/search_food`
- **Method:** `GET`
- **Query Parameters:**
  - `query` (required): The name of the food to search for.
- **Description:** Searches for food items based on the provided query.
- **Example:**
  ```bash
  curl -X GET "http://localhost:8000/search_food?query=apple"
  ```

### Get Food Nutrition

- **URL:** `/food_nutrition`
- **Method:** `GET`
- **Query Parameters:**
  - `food_id` (required): The ID of the food item from FatSecret.
- **Description:** Retrieves nutritional information for the specified food item.
- **Example:**
  ```bash
  curl -X GET "http://localhost:8000/food_nutrition?food_id=12345"
  ```

### Search Food Detail

- **URL:** `/search_food_detail`
- **Method:** `GET`
- **Query Parameters:**
  - `query` (required): The name of the food to search for.
- **Description:** Searches for food items based on the provided query and retrieves detailed nutritional information for the first result.
- **Example:**
  ```bash
  curl -X GET "http://localhost:8000/search_food_detail?query=apple"
  ```

### Search Food by ID

- **URL:** `/search_food_by_id`
- **Method:** `GET`
- **Query Parameters:**
  - `food_id` (required): The ID of the food item from FatSecret.
- **Description:** Retrieves detailed nutritional information for the specified food item.
- **Example:**
  ```bash
  curl -X GET "http://localhost:8000/search_food_by_id?food_id=12345"
  ```

## Error Handling

If an error occurs, the API will return a JSON response with an `error` field describing the issue.

## License

This project is licensed under the MIT License.